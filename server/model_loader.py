# server/model_loader.py
import os
import torch
import numpy as np
import threading
import copy
from pathlib import Path
from typing import Iterator, Optional, Dict, Tuple
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

import sys
import os

# Add the VibeVoice repository to sys.path for editable installation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "third_party", "VibeVoice")))

# VibeVoice Imports
try:
    from vibevoice.modular.modeling_vibevoice_streaming_inference import (
        VibeVoiceStreamingForConditionalGenerationInference,
    )
    from vibevoice.processor.vibevoice_streaming_processor import (
        VibeVoiceStreamingProcessor,
    )
    from vibevoice.modular.streamer import AudioStreamer
    VIBEVOICE_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: ImportError for VibeVoice: {e}")
    VIBEVOICE_AVAILABLE = False

# Load environment variables
load_dotenv()

SAMPLE_RATE = 24_000

print(f"DEBUG: sys.path at startup: {sys.path}")
print(f"DEBUG: VIBEVOICE_AVAILABLE: {VIBEVOICE_AVAILABLE}")

class VibeVoiceManager:
    def __init__(self, model_id="microsoft/VibeVoice-Realtime-0.5B"):
        self.model_id = model_id
        self.model_path = os.getenv("VIBEVOICE_MODEL_PATH", "./models/VibeVoice-Realtime-0.5B")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor: Optional[VibeVoiceStreamingProcessor] = None
        self.model: Optional[VibeVoiceStreamingForConditionalGenerationInference] = None
        self.voice_preset: Optional[torch.Tensor] = None
        self._torch_device = torch.device(self.device)

    def download_if_needed(self):
        if not os.path.exists(self.model_path) or not os.listdir(self.model_path):
            print(f"Downloading model '{self.model_id}' to '{self.model_path}'...")
            snapshot_download(repo_id=self.model_id, local_dir=self.model_path)
        else:
            print(f"Model found at '{self.model_path}'")

    def load(self):
        if not VIBEVOICE_AVAILABLE:
            print("❌ VibeVoice package not found. Please install it.")
            return False

        self.download_if_needed()

        print(f"Loading VibeVoice processor from {self.model_path}...")
        self.processor = VibeVoiceStreamingProcessor.from_pretrained(self.model_path)

        # Decide dtype & attention
        if self.device == "cuda":
            load_dtype = torch.bfloat16
            device_map = 'cuda'
            attn_impl = "flash_attention_2"
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU detected: {gpu_name}")
        else:
            load_dtype = torch.float32
            device_map = 'cpu'
            attn_impl = "sdpa"
            print("ℹ️ Running on CPU")

        print(f"Loading VibeVoice model with dtype={load_dtype}, attn={attn_impl}...")
        try:
            self.model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
                self.model_path,
                torch_dtype=load_dtype,
                device_map=device_map,
                attn_implementation=attn_impl,
            )
        except Exception as e:
            print(f"Warning: Failed to load with {attn_impl}, falling back to sdpa: {e}")
            self.model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
                self.model_path,
                torch_dtype=load_dtype,
                device_map=device_map,
                attn_implementation='sdpa',
            )

        self.model.eval()
        self.model.model.noise_scheduler = self.model.model.noise_scheduler.from_config(
            self.model.model.noise_scheduler.config,
            algorithm_type="sde-dpmsolver++",
            beta_schedule="squaredcos_cap_v2",
        )
        self.model.set_ddpm_inference_steps(num_steps=5)

        self._load_default_voice()
        return True

    def _load_default_voice(self):
        # Look for a voice preset in the third_party directory
        preset_dir = Path("third_party/VibeVoice/demo/voices/streaming_model")
        preset_path = preset_dir / "en-Carter_man.pt" # Defaulting to Carter
        
        if not preset_path.exists():
            # Try to find any .pt file in that directory
            presets = list(preset_dir.glob("*.pt"))
            if presets:
                preset_path = presets[0]
            else:
                print("⚠️ No voice presets found. TTS might fail.")
                return

        print(f"Loading voice preset from {preset_path}")
        self.voice_preset = torch.load(
            preset_path,
            map_location=self._torch_device,
            weights_only=False,
        )

    def stream_audio(self, text: str) -> Iterator[bytes]:
        if not self.model or not self.processor or not self.voice_preset:
            print("Model not loaded correctly")
            return

        text = text.replace("’", "'").strip()
        
        # Prepare inputs
        processor_kwargs = {
            "text": text,
            "cached_prompt": self.voice_preset,
            "padding": True,
            "return_tensors": "pt",
            "return_attention_mask": True,
        }
        processed = self.processor.process_input_with_cached_prompt(**processor_kwargs)
        inputs = {
            key: value.to(self._torch_device) if hasattr(value, "to") else value
            for key, value in processed.items()
        }

        audio_streamer = AudioStreamer(batch_size=1, stop_signal=None, timeout=None)
        stop_event = threading.Event()

        # Run generation in a separate thread
        def run_gen():
            try:
                self.model.generate(
                    **inputs,
                    max_new_tokens=None,
                    cfg_scale=1.5,
                    tokenizer=self.processor.tokenizer,
                    generation_config={"do_sample": False},
                    audio_streamer=audio_streamer,
                    stop_check_fn=stop_event.is_set,
                    verbose=False,
                    all_prefilled_outputs=copy.deepcopy(self.voice_preset),
                )
            except Exception as e:
                print(f"Generation error: {e}")
            finally:
                audio_streamer.end()

        thread = threading.Thread(target=run_gen, daemon=True)
        thread.start()

        try:
            stream = audio_streamer.get_stream(0)
            for audio_chunk in stream:
                if torch.is_tensor(audio_chunk):
                    audio_chunk = audio_chunk.detach().cpu().to(torch.float32).numpy()
                else:
                    audio_chunk = np.asarray(audio_chunk, dtype=np.float32)

                # Convert to PCM16
                audio_chunk = np.clip(audio_chunk, -1.0, 1.0)
                pcm = (audio_chunk * 32767.0).astype(np.int16)
                yield pcm.tobytes()
        finally:
            stop_event.set()
            thread.join()

def load_vibevoice_model():
    manager = VibeVoiceManager()
    success = manager.load()
    return (manager if success else None), manager.device
