# app/audio_client.py
import requests
import pyaudio
import threading
import queue
import time
from .settings import settings_manager

class AudioClient:
    def __init__(self, server_url="http://localhost:8000/v1/audio/stream"):
        self.server_url = server_url
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.chunk_queue = queue.Queue()
        self.is_playing = False
        
        # Audio parameters should match VibeVoice output (e.g., 24kHz or 16kHz)
        # For now, we assume 24000Hz, Mono, 16-bit PCM
        self.rate = 24000
        self.channels = 1
        self.format = pyaudio.paInt16
        
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
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None

    def stream_and_play(self, text, voice_key=None):
        """
        Requests audio stream from server and queues chunks for playback.
        Implements pre-buffering to ensure smooth playback under load.
        """
        if not text.strip():
            print("DEBUG: Empty text, skipping audio.")
            return

        print(f"DEBUG: Requesting audio for text: {text[:30]}... (Voice: {voice_key})")
        self.is_playing = True
        
        # Recalculate buffer settings (in case they changed)
        buffer_seconds = settings_manager.get("audio", "buffer_seconds") or 4.0
        bytes_per_sample = 2 # 16-bit
        buffer_min_bytes = int(self.rate * self.channels * bytes_per_sample * buffer_seconds)
        
        play_thread = None
        started_playing = False
        accumulated_bytes = 0
        chunks_received = 0

        try:
            # Increased timeout to 45s to handle model warm-up and long generation times
            payload = {"text": text}
            if voice_key:
                payload["voice_key"] = voice_key
                
            response = requests.post(self.server_url, json=payload, stream=True, timeout=45)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    self.chunk_queue.put(chunk)
                    accumulated_bytes += len(chunk)
                    chunks_received += 1
                    
                    # Check if we should start playing (Buffer filled)
                    if not started_playing and accumulated_bytes >= buffer_min_bytes:
                        print(f"DEBUG: Buffer filled ({accumulated_bytes} bytes). Starting playback.")
                        play_thread = threading.Thread(target=self._play_worker)
                        play_thread.start()
                        started_playing = True

            print(f"DEBUG: Finished receiving audio. Total chunks: {chunks_received}")
            
            # Stream finished. If playback hasn't started yet (e.g. short audio), start now.
            if not started_playing:
                print(f"DEBUG: Stream finished before buffer fill ({accumulated_bytes} bytes). Starting playback immediately.")
                play_thread = threading.Thread(target=self._play_worker)
                play_thread.start()
                started_playing = True

        except Exception as e:
            print(f"Audio client error: {e}")
        finally:
            self.is_playing = False
            if play_thread:
                play_thread.join()
                print("DEBUG: Audio playback thread joined.")
            else:
                print("DEBUG: Audio playback thread was never started.")

    def __del__(self):
        self.p.terminate()
