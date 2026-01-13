# app/main.py
import os
import sys
import subprocess
import time
import requests
import datetime
import threading
from dotenv import load_dotenv
from PIL import Image
import pystray
from global_hotkeys import register_hotkeys, start_checking_hotkeys, stop_checking_hotkeys

from .capture import ScreenCapturer
from .vision import VisionEngine
from .audio_client import AudioClient

# Load configuration
load_dotenv()

import winsound

class ScreenBanterApp:
    def __init__(self):
        self.capturer = ScreenCapturer()
        self.vision = VisionEngine()
        self.audio = AudioClient()
        self.icon = None
        self.server_process = None
        self.screenshot_queue = []
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log_ocr_result(self, text):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(self.log_dir, "ocr.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"--- {timestamp} ---\n")
            f.write(text)
            f.write("\n\n")

    def play_capture_sound(self):
        """
        Plays a short chime/feedback sound for capture confirmation.
        This runs in a separate thread to be non-blocking.
        """
        def _play():
            try:
                # Beep at 1500 Hz for 100 ms
                winsound.Beep(1500, 100)
            except Exception as e:
                print(f"Failed to play capture sound: {e}")
        threading.Thread(target=_play, daemon=True).start()

    def start_tts_server(self):
        print("Checking for existing TTS server...")
        try:
            resp = requests.get("http://localhost:8000/health", timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    print(f"TTS Server already running! (Device: {data.get('device')})")
                    return True
        except requests.RequestException:
            pass

        print("Starting TTS server...")
        cmd = ["uv", "run", "uvicorn", "server.tts_server:app", "--port", "8000"]
        try:
            self.server_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE
            )
            
            print("Waiting for TTS server to be ready...")
            max_retries = 60
            for i in range(max_retries):
                try:
                    resp = requests.get("http://localhost:8000/health", timeout=1)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "ok":
                            print(f"TTS Server ready! (Device: {data.get('device')})")
                            return True
                except requests.RequestException:
                    pass
                
                if self.server_process.poll() is not None:
                    _, stderr = self.server_process.communicate()
                    print(f"TTS Server failed to start. Error: {stderr.decode()}")
                    return False
                
                time.sleep(1)
                
            print("Timeout waiting for TTS server.")
            return False
            
        except Exception as e:
            print(f"Failed to start TTS server: {e}")
            return False

    def stop_tts_server(self):
        if self.server_process:
            print("Stopping TTS server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None

    def on_trigger(self):
        """Ctrl + Alt + S: Instant capture and narrate."""
        print("DEBUG: Instant trigger pressed.")
        self.screenshot_queue = [] # Clear queue for instant trigger
        self.on_queue_screenshot()
        self.on_process_queue()

    def on_queue_screenshot(self):
        """F10: Capture and queue."""
        print("DEBUG: Queueing screenshot...")
        try:
            frame = self.capturer.capture()
            if frame is not None:
                self.screenshot_queue.append(frame)
                print(f"DEBUG: Screenshot added to queue. Queue size: {len(self.screenshot_queue)}")
                self.play_capture_sound()
            else:
                print("DEBUG: Failed to capture screen.")
        except Exception as e:
            print(f"ERROR in on_queue_screenshot: {e}")

    def on_process_queue(self):
        """F11: Process all queued screenshots."""
        if not self.screenshot_queue:
            print("DEBUG: Queue is empty.")
            return

        print(f"DEBUG: Processing queue of {len(self.screenshot_queue)} images...")
        try:
            # If it's a single image, vision engine handles it
            # If it's multiple, vision engine handles that too
            input_data = self.screenshot_queue if len(self.screenshot_queue) > 1 else self.screenshot_queue[0]
            
            text = self.vision.extract_text(input_data)
            self.screenshot_queue = [] # Clear after sending
            
            if text and text.lower() != "no text identified":
                print(f"DEBUG: OCR Result: {text[:100]}...")
                self.log_ocr_result(text)
                self.audio.stream_and_play(text)
            else:
                print("DEBUG: No text identified in queue.")
        except Exception as e:
            print(f"ERROR in on_process_queue: {e}")
            import traceback
            traceback.print_exc()

    def play_startup_sound(self):
        def _play():
            try:
                tts_msg = "Screen Banter is active. F 10 to queue, F 11 to narrate queue."
                self.audio.stream_and_play(tts_msg)
            except Exception as e:
                print(f"Failed to play startup sound: {e}")
        
        threading.Thread(target=_play, daemon=True).start()

    def setup_app(self, icon):
        icon.title = "ScreenBanter: Starting Server..."
        
        if self.start_tts_server():
            icon.title = "ScreenBanter: Active"
            
            print("Registering hotkeys...")
            bindings = [
                ["control + alt + s", None, self.on_trigger],
                ["f10", None, self.on_queue_screenshot],
                ["f11", None, self.on_process_queue],
            ]
            register_hotkeys(bindings)
            start_checking_hotkeys()

            ready_msg = "ScreenBanter is active. F10 to queue, F11 to narrate queue, Ctrl+Alt+S for instant."
            print(ready_msg)
            
            self.play_startup_sound()
        else:
            icon.title = "ScreenBanter: Server Failed"
            print("Server failed to start. Check logs.")

    def run(self):
        try:
            image = Image.open("assets/icon.png")
        except FileNotFoundError:
            image = Image.new('RGB', (64, 64), color=(73, 109, 137))
            
        menu = pystray.Menu(pystray.MenuItem('Exit', self.on_exit))
        self.icon = pystray.Icon("ScreenBanter", image, "ScreenBanter: Initializing...", menu)

        self.icon.run(setup=self.setup_app)

    def on_exit(self, icon):
        print("Exiting...")
        stop_checking_hotkeys()
        self.stop_tts_server()
        icon.stop()
        sys.exit(0)

if __name__ == "__main__":
    app = ScreenBanterApp()
    app.run()
