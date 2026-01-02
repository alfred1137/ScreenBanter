# app/audio_client.py
import requests
import pyaudio
import threading
import queue

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
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True
        )
        
        while self.is_playing or not self.chunk_queue.empty():
            try:
                chunk = self.chunk_queue.get(timeout=0.1)
                self.stream.write(chunk)
            except queue.Empty:
                continue
        
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None

    def stream_and_play(self, text):
        """
        Requests audio stream from server and queues chunks for playback.
        """
        if not text.strip():
            return

        self.is_playing = True
        play_thread = threading.Thread(target=self._play_worker)
        play_thread.start()

        try:
            response = requests.post(self.server_url, json={"text": text}, stream=True)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    self.chunk_queue.put(chunk)
        except Exception as e:
            print(f"Audio client error: {e}")
        finally:
            self.is_playing = False
            play_thread.join()

    def __del__(self):
        self.p.terminate()
