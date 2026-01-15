# server/model_loader.py
import os
import torch
import numpy as np
import threading
import copy
import traceback
from pathlib import Path
from typing import Iterator, Optional, Dict, Tuple, Any, Callable, List
from huggingface_hub import snapshot_download
from transformers import BitsAndBytesConfig
from dotenv import load_dotenv

import sys

# Add the VibeVoice repository to sys.path for editable installation
VIBEVOICE_REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "third_party", "VibeVoice"))
if VIBEVOICE_REPO_PATH not in sys.path:
    sys.path.insert(0, VIBEVOICE_REPO_PATH)

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

class DictWithAttrs(dict):
    """
    A dictionary that allows access to keys as attributes.
    Used to wrap converted ModelOutput dictionaries.
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

class VibeVoiceManager:
    """
    Manages the VibeVoice TTS model, aligned with the official demo's StreamingTTSService.
    """
    def __init__(self, model_id="microsoft/VibeVoice-Realtime-0.5B"):
        self.model_id = model_id
        self.model_path = os.getenv("VIBEVOICE_MODEL_PATH", "./models/VibeVoice-Realtime-0.5B")
        self.inference_steps = 5
        self.sample_rate = SAMPLE_RATE
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._torch_device = torch.device(self.device)
        
        self.processor: Optional[VibeVoiceStreamingProcessor] = None
        self.model: Optional[VibeVoiceStreamingForConditionalGenerationInference] = None
        self.voice_presets: Dict[str, Path] = {}
        self.default_voice_key: Optional[str] = None
        self._voice_cache: Dict[str, Any] = {}

    def download_if_needed(self):
        if not os.path.exists(self.model_path) or not os.listdir(self.model_path):
            print(f"Downloading model '{self.model_id}' to '{self.model_path}'...")
            snapshot_download(repo_id=self.model_id, local_dir=self.model_path)
        else:
            print(f"Model found at '{self.model_path}'")

    def load(self):
        if not VIBEVOICE_AVAILABLE:
            print("❌ VibeVoice package not found. Please check sys.path and installation.")
            return False

        self.download_if_needed()

        print(f"[startup] Loading processor from {self.model_path}")
        self.processor = VibeVoiceStreamingProcessor.from_pretrained(self.model_path)

        # Decide dtype & attention (Mirroring official demo logic)
        load_in_4bit = os.getenv("LOAD_IN_4BIT", "true").lower() == "true"
        quantization_config = None

        if self.device == "cuda":
            # Optimization: Use float16 for better Tensor Core utilization on RTX cards
            load_dtype = torch.float16
            device_map = 'cuda'
            attn_impl = "flash_attention_2"
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU detected: {gpu_name}")

            if load_in_4bit:
                print(f"⚡ 4-bit Quantization Enabled (BitsAndBytes)")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
        else:
            load_dtype = torch.float32
            device_map = 'cpu'
            attn_impl = "sdpa"
            print("ℹ️ Running on CPU")

        print(f"Using device: {device_map}, torch_dtype: {load_dtype}, attn_implementation: {attn_impl}")
        
        try:
            self.model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
                self.model_path,
                torch_dtype=load_dtype,
                device_map=device_map,
                attn_implementation=attn_impl,
                quantization_config=quantization_config,
            )
        except Exception as e:
            if attn_impl == 'flash_attention_2':
                print(f"Warning: FlashAttention2 failed, falling back to SDPA: {e}")
                self.model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
                    self.model_path,
                    torch_dtype=load_dtype,
                    device_map=device_map,
                    attn_implementation='sdpa',
                    quantization_config=quantization_config,
                )
                print("Load model with SDPA successful")
            else:
                print(f"Fatal error loading model: {e}")
                return False

        self.model.eval()

        # Noise scheduler config (Mandatory in official demo)
        self.model.model.noise_scheduler = self.model.model.noise_scheduler.from_config(
            self.model.model.noise_scheduler.config,
            algorithm_type="sde-dpmsolver++",
            beta_schedule="squaredcos_cap_v2",
        )
        self.model.set_ddpm_inference_steps(num_steps=self.inference_steps)

        # Voice Presets (Mirroring official demo)
        self._load_voice_presets()
        return True

    def _load_voice_presets(self):
        voices_dir = Path(VIBEVOICE_REPO_PATH) / "demo" / "voices" / "streaming_model"
        if not voices_dir.exists():
            print(f"⚠️ Voices directory not found: {voices_dir}")
            return

        for pt_path in voices_dir.rglob("*.pt"):
            self.voice_presets[pt_path.stem] = pt_path

        if not self.voice_presets:
            print(f"⚠️ No voice presets (.pt) found in {voices_dir}")
            return

        # Default to en-Carter_man if available, otherwise first one found
        if "en-Carter_man" in self.voice_presets:
            self.default_voice_key = "en-Carter_man"
        else:
            self.default_voice_key = next(iter(self.voice_presets))
            
        print(f"[startup] Found {len(self.voice_presets)} voice presets. Default: {self.default_voice_key}")

    def get_available_voices(self) -> List[str]:
        """Returns a list of available voice keys."""
        return sorted(list(self.voice_presets.keys()))

    def _cast_recursive(self, obj, target_dtype):
        if torch.is_tensor(obj):
            if obj.is_floating_point():
                return obj.to(device=self._torch_device, dtype=target_dtype)
            else:
                return obj.to(device=self._torch_device)
        elif isinstance(obj, dict):
            new_data = {}
            # robustly gather all fields/keys
            keys = set(obj.keys())
            if hasattr(obj, "__dict__"):
                keys.update(k for k in obj.__dict__ if not k.startswith("_"))
            
            for k in keys:
                try:
                    val = obj[k] if k in obj else getattr(obj, k)
                    new_data[k] = self._cast_recursive(val, target_dtype)
                except Exception:
                    continue # Skip inaccessible keys
            return DictWithAttrs(new_data)
        elif isinstance(obj, list):
            return [self._cast_recursive(v, target_dtype) for v in obj]
        elif isinstance(obj, tuple):
            return tuple(self._cast_recursive(v, target_dtype) for v in obj)
        
        # Handle Transformers DynamicCache (past_key_values container)
        if type(obj).__name__ == "DynamicCache":
             if hasattr(obj, "key_cache"):
                 obj.key_cache = self._cast_recursive(obj.key_cache, target_dtype)
             if hasattr(obj, "value_cache"):
                 obj.value_cache = self._cast_recursive(obj.value_cache, target_dtype)
             return obj
             
        return obj

    def _ensure_voice_cached(self, key: str):
        if key not in self.voice_presets:
            raise RuntimeError(f"Voice preset {key!r} not found")

        if key not in self._voice_cache:
            preset_path = self.voice_presets[key]
            print(f"Loading voice preset {key} from {preset_path}")
            prefilled_outputs = torch.load(
                preset_path,
                map_location=self._torch_device,
                weights_only=False,
            )
            
            # Determine target dtype based on device configuration
            target_dtype = torch.float16 if self.device == "cuda" else torch.float32
            prefilled_outputs = self._cast_recursive(prefilled_outputs, target_dtype)

            self._voice_cache[key] = prefilled_outputs

        return self._voice_cache[key]

    def _prepare_inputs(self, text: str, prefilled_outputs: Any):
        if not self.processor or not self.model:
            raise RuntimeError("VibeVoiceManager not initialized")

        processor_kwargs = {
            "text": text.strip(),
            "cached_prompt": prefilled_outputs,
            "padding": True,
            "return_tensors": "pt",
            "return_attention_mask": True,
        }
        processed = self.processor.process_input_with_cached_prompt(**processor_kwargs)
        prepared = {
            key: value.to(self._torch_device) if hasattr(value, "to") else value
            for key, value in processed.items()
        }
        return prepared

    def _run_generation(
        self,
        inputs: Dict[str, Any],
        audio_streamer: AudioStreamer,
        errors: List[Exception],
        cfg_scale: float,
        prefilled_outputs: Any,
        stop_event: threading.Event,
    ):
        try:
            print(f"DEBUG: Starting model.generate...")
            self.model.generate(
                **inputs,
                max_new_tokens=None,
                cfg_scale=cfg_scale,
                tokenizer=self.processor.tokenizer,
                generation_config={"do_sample": False},
                audio_streamer=audio_streamer,
                stop_check_fn=stop_event.is_set,
                verbose=False,
                refresh_negative=True,
                all_prefilled_outputs=copy.deepcopy(prefilled_outputs),
            )
            print(f"DEBUG: model.generate finished.")
        except Exception as exc:
            print(f"DEBUG: model.generate failed: {exc}")
            errors.append(exc)
            traceback.print_exc()
        finally:
            audio_streamer.end()

    def stream_audio(self, text: str, voice_key: Optional[str] = None, cfg_scale: float = 1.5) -> Iterator[bytes]:
        """
        Streams audio for the given text. Yields PCM16 bytes.
        """
        if not text.strip() or not self.model:
            return

        print(f"DEBUG: stream_audio called for text length: {len(text)}")
        text = text.replace("’", "'")
        key = voice_key if voice_key in self.voice_presets else self.default_voice_key
        if not key:
            print("No voice preset available")
            return

        prefilled_outputs = self._ensure_voice_cached(key)
        inputs = self._prepare_inputs(text, prefilled_outputs)
        
        audio_streamer = AudioStreamer(batch_size=1, stop_signal=None, timeout=None)
        errors = []
        stop_event = threading.Event()

        thread = threading.Thread(
            target=self._run_generation,
            args=(inputs, audio_streamer, errors, cfg_scale, prefilled_outputs, stop_event),
            daemon=True
        )
        thread.start()

        try:
            stream = audio_streamer.get_stream(0)
            first_chunk = True
            for audio_chunk in stream:
                if first_chunk:
                    print("DEBUG: First audio chunk received from streamer.")
                    first_chunk = False
                    
                if torch.is_tensor(audio_chunk):
                    audio_chunk = audio_chunk.detach().cpu().to(torch.float32).numpy()
                else:
                    audio_chunk = np.asarray(audio_chunk, dtype=np.float32)

                if audio_chunk.ndim > 1:
                    audio_chunk = audio_chunk.reshape(-1)

                # PCM16 conversion
                audio_chunk = np.clip(audio_chunk, -1.0, 1.0)
                pcm = (audio_chunk * 32767.0).astype(np.int16)
                yield pcm.tobytes()
                
        finally:
            stop_event.set()
            audio_streamer.end()
            thread.join()
            if errors:
                raise errors[0]

def load_vibevoice_model():
    manager = VibeVoiceManager()
    success = manager.load()
    return (manager if success else None), manager.device
