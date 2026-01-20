# app/main.py
import os
import sys
import subprocess
import time
import requests
import datetime
import threading
import ctypes
from dotenv import load_dotenv
from PIL import Image
import pystray
from global_hotkeys import register_hotkeys, start_checking_hotkeys, stop_checking_hotkeys

from .capture import ScreenCapturer
from .vision import VisionEngine
from .audio_client import AudioClient
from .settings import settings_manager
from .hud_window import BanterHUD

# Load configuration
load_dotenv()

import winsound

class ScreenBanterApp:
    def __init__(self):
        self.set_process_priority()
        self.capturer = ScreenCapturer()
        self.vision = VisionEngine()
        self.audio = AudioClient()
        self.icon = None
        self.server_process = None
        self.stdout_log = None
        self.stderr_log = None
        self.screenshot_queue = []
        self.hud = None
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def set_process_priority(self):
        """
        Sets the process priority based on user settings.
        Default is ABOVE_NORMAL_PRIORITY_CLASS (0x00008000).
        """
        priority_map = {
            "normal": 0x00000020,
            "above_normal": 0x00008000,
            "high": 0x00000080
        }
        
        setting = settings_manager.get("system", "priority") or "above_normal"
        priority_class = priority_map.get(setting.lower(), 0x00008000)

        try:
            # Set argtypes and restype for Windows API calls for reliability
            ctypes.windll.kernel32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            ctypes.windll.kernel32.SetPriorityClass.restype = ctypes.c_bool
            ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p

            handle = ctypes.windll.kernel32.GetCurrentProcess()
            if ctypes.windll.kernel32.SetPriorityClass(handle, priority_class):
                print(f"DEBUG: Process priority set to {setting.upper()}.")
            else:
                print(f"DEBUG: Failed to set process priority.")
        except Exception as e:
            print(f"DEBUG: Error setting process priority: {e}")

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
        if not settings_manager.is_local_tts_supported():
            print("DEBUG: Local TTS dependencies not found. Cannot start local server.")
            return False

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

            # Prepare Environment for Server
            server_env = os.environ.copy()
            
            # Apply Performance Mode Settings
            perf_enabled = settings_manager.get("performance_mode", "enabled")
            quant_mode = settings_manager.get("performance_mode", "quantization")
            
            # Logic: If Performance Mode is Enabled AND Quantization is '4bit', set env var
            # If Performance Mode is Disabled, force 4-bit OFF (unless default behavior changes)
            if perf_enabled and quant_mode == "4bit":
                server_env["LOAD_IN_4BIT"] = "true"
                print("DEBUG: Launching Server with LOAD_IN_4BIT=true")
            else:
                server_env["LOAD_IN_4BIT"] = "false"
                print(f"DEBUG: Launching Server with LOAD_IN_4BIT=false (Mode: {perf_enabled}, Quant: {quant_mode})")

            self.server_process = subprocess.Popen(
                cmd, 
                stdout=self.stdout_log, 
                stderr=self.stderr_log,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                env=server_env
            )
            
            print("Waiting for TTS server to be ready...")
            max_retries = 120
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
            region = None
            if settings_manager.get("capture", "use_region"):
                region = settings_manager.get("capture", "region")
                if region:
                    print(f"DEBUG: Capturing region: {region}")

            frame = self.capturer.capture(region=region)
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

        # Snapshot the queue to process and clear the main queue immediately
        # This allows the user to capture new screenshots while the previous batch is processing
        images_to_process = list(self.screenshot_queue)
        self.screenshot_queue = [] 
        
        print(f"DEBUG: Processing queue of {len(images_to_process)} images in background...")

        def _process_task(images):
            try:
                hud_enabled = settings_manager.get("hud", "enabled")

                # Update HUD: Scanning
                if self.hud and hud_enabled:
                    self.hud.safe_show_message("Scanning screen...", status="Vision Processing")

                # If it's a single image, vision engine handles it
                # If it's multiple, vision engine handles that too
                input_data = images if len(images) > 1 else images[0]
                
                text = self.vision.extract_text(input_data)
                
                if text and text.lower() != "no text identified":
                    print(f"DEBUG: OCR Result: {text[:100]}...")
                    self.log_ocr_result(text)
                    
                    # Update HUD: Text Found
                    if self.hud and hud_enabled:
                        self.hud.safe_show_message(text, status="Generating Voice...")
                    
                    voice_key = settings_manager.get_audio_config().get("voice_key")
                    
                    # Update HUD: Speaking (approximate, since stream_and_play is blocking-ish or streaming)
                    # We can assume it starts speaking quickly.
                    if self.hud and hud_enabled:
                        self.hud.safe_update_status("Speaking...")
                        
                    self.audio.stream_and_play(text, voice_key=voice_key)
                    
                    # Dismiss HUD after playback
                    if self.hud and hud_enabled:
                        self.hud.safe_dismiss(delay=3.0)
                else:
                    print("DEBUG: No text identified in queue.")
                    if self.hud and hud_enabled:
                        self.hud.safe_show_message("No text found.", status="Idle")
                        self.hud.safe_dismiss(delay=2.0)
            except Exception as e:
                print(f"ERROR in processing task: {e}")
                if self.hud and hud_enabled:
                    self.hud.safe_show_message(f"Error: {e}", status="Error")
                    self.hud.safe_dismiss(delay=5.0)
                import traceback
                traceback.print_exc()

        # Run OCR and TTS in a separate thread to avoid blocking the hotkey listener
        threading.Thread(target=_process_task, args=(images_to_process,), daemon=True).start()

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
        tts_provider = settings_manager.get("audio", "tts_provider") or "local"
        
        success = True
        if tts_provider == "local":
            if not settings_manager.is_local_tts_supported():
                print("WARNING: Local TTS is selected but dependencies are missing (Lite version).")
                if self.icon:
                    self.icon.notify("Local TTS not supported in this version. Switching to Cloud.", "Lite Version Active")
                # Fallback to gemini if local is not available
                settings_manager.set("audio", "tts_provider", "gemini")
                tts_provider = "gemini"
            else:
                success = self.start_tts_server()
        
        if tts_provider != "local":
            print(f"DEBUG: Skipping local TTS server as provider is '{tts_provider}'")

        if success:
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

    def init_hud(self):
        """Starts the HUD in a separate thread."""
        def run_hud_thread():
            print("DEBUG: Starting HUD thread...")
            try:
                self.hud = BanterHUD()
                self.hud.mainloop()
            except Exception as e:
                print(f"HUD Error: {e}")

        threading.Thread(target=run_hud_thread, daemon=True).start()

    def setup_app(self, icon):
        icon.visible = True
        icon.title = "ScreenBanter: Starting Server..."
        
        # Start HUD immediately
        self.init_hud()
        
        # Run initialization in a separate thread so the icon appears immediately
        threading.Thread(target=self.init_backend, daemon=True).start()

    def on_settings(self, icon=None):
        """Opens the settings window via the HUD."""
        if self.hud:
            self.hud.open_settings()
        else:
            print("HUD not initialized, cannot open settings.")

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
