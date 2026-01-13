# app/audio_client.py
import requests
import pyaudio
import threading
import queue
import time

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

    def stream_and_play(self, text):
        """
        Requests audio stream from server and queues chunks for playback.
        """
        if not text.strip():
            print("DEBUG: Empty text, skipping audio.")
            return

        print(f"DEBUG: Requesting audio for text: {text[:30]}...")
        self.is_playing = True
        play_thread = threading.Thread(target=self._play_worker)
        play_thread.start()

        chunks_received = 0
        try:
            # Increased timeout to 45s to handle model warm-up and long generation times
            response = requests.post(self.server_url, json={"text": text}, stream=True, timeout=45)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    self.chunk_queue.put(chunk)
                    chunks_received += 1
            print(f"DEBUG: Finished receiving audio. Total chunks: {chunks_received}")
        except Exception as e:
            print(f"Audio client error: {e}")
        finally:
            self.is_playing = False
            play_thread.join()
            print("DEBUG: Audio playback thread joined.")

    def __del__(self):
        self.p.terminate()
