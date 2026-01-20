# app/audio_client.py
import requests
import pyaudio
import threading
import queue
import time
import os
from .settings import settings_manager
from google import genai
from google.genai import types

class AudioClient:
    def __init__(self, server_url="http://localhost:8000/v1/audio/stream"):
        self.server_url = server_url
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.chunk_queue = queue.Queue()
        self.is_playing = False
        self._lock = threading.Lock()
        
        # Audio parameters should match VibeVoice output (e.g., 24kHz or 16kHz)
        # For now, we assume 24000Hz, Mono, 16-bit PCM
        self.rate = 24000
        self.channels = 1
        self.format = pyaudio.paInt16

        # Cloud TTS Client
        self.genai_client = None
        api_key = os.getenv("GEMINI_KEY")
        if api_key:
            self.genai_client = genai.Client(api_key=api_key)
        
    def _play_worker(self):
        """
        Background worker that plays chunks from the queue.
        """
        print("DEBUG: Audio playback worker started.")
        try:
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                output=True
            )
            
            chunks_played = 0
            # Play as long as we are "playing" OR there is still data in the queue
            while self.is_playing or not self.chunk_queue.empty():
                try:
                    chunk = self.chunk_queue.get(timeout=0.1)
                    self.stream.write(chunk)
                    chunks_played += 1
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"DEBUG: Error writing audio chunk: {e}")
                    break
            
            print(f"DEBUG: Audio playback worker finished. Chunks played: {chunks_played}")
        except Exception as e:
            print(f"DEBUG: Audio playback worker error: {e}")
        finally:
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
                self.stream = None

    def stream_and_play(self, text, voice_key=None):
        """
        Requests audio from TTS provider and queues chunks for playback.
        Ensures only one narration happens at a time.
        """
        if not text.strip():
            print("DEBUG: Empty text, skipping audio.")
            return

        with self._lock:
            tts_provider = settings_manager.get("audio", "tts_provider") or "local"
            print(f"DEBUG: Using TTS Provider: {tts_provider}")

            if tts_provider == "gemini":
                self._stream_from_gemini(text)
            else:
                self._stream_from_local(text, voice_key)

    def _stream_from_gemini(self, text):
        if not self.genai_client:
            print("ERROR: Gemini client not initialized. Check GEMINI_KEY.")
            return

        print(f"DEBUG: Requesting Gemini Cloud TTS for text: {text[:50]}...")
        self.is_playing = True
        play_thread = None

        try:
            model_id = settings_manager.get("audio", "cloud_model") or "gemini-2.5-flash-preview-tts"
            voice_name = settings_manager.get("audio", "cloud_voice") or "Puck"

            # Use generate_content with audio modality
            response = self.genai_client.models.generate_content(
                model=model_id,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    )
                )
            )

            if response.candidates and response.candidates[0].content.parts:
                # The correct path according to documentation is response.candidates[0].content.parts[0].inline_data.data
                part = response.candidates[0].content.parts[0]
                if hasattr(part, 'inline_data') and part.inline_data:
                    audio_data = part.inline_data.data
                    
                    # Check if it looks like WAV (starts with 'RIFF')
                    if audio_data.startswith(b'RIFF'):
                        print("DEBUG: Received WAV format from Gemini. Stripping 44-byte header.")
                        audio_data = audio_data[44:]
                    
                    chunk_size = 4096
                    for i in range(0, len(audio_data), chunk_size):
                        self.chunk_queue.put(audio_data[i:i + chunk_size])
                    
                    print(f"DEBUG: Received {len(audio_data)} bytes of audio from Gemini.")
                    play_thread = threading.Thread(target=self._play_worker, daemon=True)
                    play_thread.start()
                else:
                    print(f"DEBUG: Part does not contain inline_data. Part attributes: {dir(part)}")
            else:
                print("DEBUG: No candidates or parts in Gemini response.")

        except Exception as e:
            print(f"Gemini Cloud TTS error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # We must wait for the playback to finish before releasing the lock or changing status
            if play_thread:
                # Signal the worker that no more data is coming (after it drains the queue)
                self.is_playing = False 
                play_thread.join()
                print("DEBUG: Gemini audio playback finished.")
            else:
                self.is_playing = False


    def _stream_from_local(self, text, voice_key):
        print(f"DEBUG: Requesting local audio for text: {text[:50]}... (Voice: {voice_key})")
        self.is_playing = True
        play_thread = None

        # Get playback mode from settings
        playback_mode = settings_manager.get("audio", "playback_mode") or "stream"

        try:
            payload = {"text": text}
            if voice_key:
                payload["voice_key"] = voice_key

            # Increased timeout to 45s to handle model warm-up and long generation times
            response = requests.post(self.server_url, json=payload, stream=True, timeout=45)
            response.raise_for_status()

            if playback_mode == "stream":
                # --- STREAMING LOGIC ---
                print("DEBUG: Playback mode: stream")
                buffer_seconds = settings_manager.get("audio", "buffer_seconds") or 4.0
                bytes_per_sample = 2  # 16-bit
                buffer_min_bytes = int(self.rate * self.channels * bytes_per_sample * buffer_seconds)

                started_playing = False
                accumulated_bytes = 0
                chunks_received = 0

                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        self.chunk_queue.put(chunk)
                        accumulated_bytes += len(chunk)
                        chunks_received += 1

                        if not started_playing and accumulated_bytes >= buffer_min_bytes:
                            print(f"DEBUG: Buffer filled ({accumulated_bytes} bytes). Starting playback.")
                            play_thread = threading.Thread(target=self._play_worker, daemon=True)
                            play_thread.start()
                            started_playing = True

                print(f"DEBUG: Finished receiving audio stream. Total chunks: {chunks_received}")

                if not started_playing and not self.chunk_queue.empty():
                    print(f"DEBUG: Stream finished before buffer fill ({accumulated_bytes} bytes). Starting playback.")
                    play_thread = threading.Thread(target=self._play_worker, daemon=True)
                    play_thread.start()

            elif playback_mode == "pre-generate":
                # --- PRE-GENERATE LOGIC ---
                print("DEBUG: Playback mode: pre-generate. Downloading full audio.")
                chunks_received = 0
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        self.chunk_queue.put(chunk)
                        chunks_received += 1

                print(f"DEBUG: Full audio downloaded. Total chunks: {chunks_received}. Starting playback.")
                if not self.chunk_queue.empty():
                    play_thread = threading.Thread(target=self._play_worker, daemon=True)
                    play_thread.start()

        except Exception as e:
            print(f"Audio client error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Signal the worker and wait
            if play_thread:
                self.is_playing = False
                play_thread.join()
                print("DEBUG: Local audio playback finished.")
            else:
                self.is_playing = False
                # Ensure queue is cleared if playback never started
                while not self.chunk_queue.empty():
                    try:
                        self.chunk_queue.get_nowait()
                    except queue.Empty:
                        break
                print("DEBUG: Audio playback thread was not started or an error occurred.")

    def __del__(self):
        self.p.terminate()
