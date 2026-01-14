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
from .settings import settings_manager

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
        self.stdout_log = None
        self.stderr_log = None
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
        
        # Check if we are running in a frozen bundle (Nuitka/PyInstaller)
        if getattr(sys, 'frozen', False):
            # If frozen, we spawn ourselves with the --server flag
            cmd = [sys.executable, "--server"]
        else:
            # Development mode: use current python environment directly
            cmd = [sys.executable, "-m", "uvicorn", "server.tts_server:app", "--port", "8000"]

        try:
            # Redirect logs to files for debugging
            self.stdout_log = open(os.path.join(self.log_dir, "server_stdout.log"), "w")
            self.stderr_log = open(os.path.join(self.log_dir, "server_stderr.log"), "w")

            self.server_process = subprocess.Popen(
                cmd, 
                stdout=self.stdout_log, 
                stderr=self.stderr_log,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
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
                    print("TTS Server failed to start.")
                    print(f"Check logs in {self.log_dir}/server_stderr.log for details.")
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
            
        if self.stdout_log:
            self.stdout_log.close()
            self.stdout_log = None
        if self.stderr_log:
            self.stderr_log.close()
            self.stderr_log = None

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
                
                voice_key = settings_manager.get_audio_config().get("voice_key")
                self.audio.stream_and_play(text, voice_key=voice_key)
            else:
                print("DEBUG: No text identified in queue.")
        except Exception as e:
            print(f"ERROR in on_process_queue: {e}")
            import traceback
            traceback.print_exc()

    def play_startup_sound(self):
        if not settings_manager.get("system", "play_startup_sound"):
            return

        def _play():
            try:
                tts_msg = "Screen Banter is active. Check settings for controls."
                voice_key = settings_manager.get_audio_config().get("voice_key")
                self.audio.stream_and_play(tts_msg, voice_key=voice_key)
            except Exception as e:
                print(f"Failed to play startup sound: {e}")
        
        threading.Thread(target=_play, daemon=True).start()

    def init_backend(self):
        """
        Background initialization task to start the server and register hotkeys
        without blocking the UI thread.
        """
        if self.start_tts_server():
            if self.icon:
                self.icon.title = "ScreenBanter: Active"
                self.icon.notify("ScreenBanter is ready!", "Startup Complete")
            
            print("Registering hotkeys...")
            
            # Load hotkeys from settings
            trigger_key = settings_manager.get_hotkey("trigger")
            queue_key = settings_manager.get_hotkey("queue")
            process_key = settings_manager.get_hotkey("process")
            
            print(f"  Trigger: {trigger_key}")
            print(f"  Queue: {queue_key}")
            print(f"  Process: {process_key}")

            bindings = [
                [trigger_key, None, self.on_trigger],
                [queue_key, None, self.on_queue_screenshot],
                [process_key, None, self.on_process_queue],
            ]
            
            try:
                register_hotkeys(bindings)
                start_checking_hotkeys()
                
                ready_msg = f"ScreenBanter is active.\n{queue_key} to queue, {process_key} to narrate queue, {trigger_key} for instant."
                print(ready_msg)
                
                self.play_startup_sound()
            except Exception as e:
                print(f"Error registering hotkeys: {e}")
                if self.icon:
                    self.icon.notify(f"Hotkey Error: {e}", "Error")

        else:
            if self.icon:
                self.icon.title = "ScreenBanter: Server Failed"
                self.icon.notify("Failed to start TTS Server.", "Startup Error")
            print("Server failed to start. Check logs.")

    def setup_app(self, icon):
        icon.visible = True
        icon.title = "ScreenBanter: Starting Server..."
        # Run initialization in a separate thread so the icon appears immediately
        threading.Thread(target=self.init_backend, daemon=True).start()

    def on_settings(self, icon=None):
        """Opens the settings window."""
        from .settings_window import SettingsWindow
        
        def _open_gui():
            # Check if window already exists (simple prevention)
            if hasattr(self, 'settings_win') and self.settings_win.winfo_exists():
                self.settings_win.focus()
                return
                
            self.settings_win = SettingsWindow()
            self.settings_win.mainloop()

        # Run GUI in a separate thread to not block the icon/hotkeys
        threading.Thread(target=_open_gui, daemon=True).start()

    def run(self):
        try:
            image = Image.open("assets/icon.png")
        except FileNotFoundError:
            image = Image.new('RGB', (64, 64), color=(73, 109, 137))
            
        menu = pystray.Menu(
            pystray.MenuItem('Settings', self.on_settings),
            pystray.MenuItem('Exit', self.on_exit)
        )
        self.icon = pystray.Icon("ScreenBanter", image, "ScreenBanter: Initializing...", menu)

        self.icon.run(setup=self.setup_app)

    def on_exit(self, icon):
        print("Exiting...")
        stop_checking_hotkeys()
        self.stop_tts_server()
        icon.stop()
        sys.exit(0)

def run_server_mode():
    """Runs the FastAPI server directly using uvicorn."""
    import uvicorn
    # Import the app object to ensure it's loaded
    from server.tts_server import app as fastapi_app
    print("Starting Internal TTS Server...")
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    if "--server" in sys.argv:
        run_server_mode()
    else:
        app = ScreenBanterApp()
        app.run()
