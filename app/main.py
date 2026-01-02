# app/main.py
import os
import sys
from dotenv import load_dotenv
from PIL import Image
import pystray
from global_hotkeys import register_hotkeys, start_checking_hotkeys, stop_checking_hotkeys

from .capture import ScreenCapturer
from .vision import VisionEngine
from .audio_client import AudioClient

# Load configuration
load_dotenv()

class ScreenBanterApp:
    def __init__(self):
        self.capturer = ScreenCapturer()
        self.vision = VisionEngine()
        self.audio = AudioClient()
        self.icon = None

    def on_trigger(self):
        print("Triggered! Capturing screen...")
        frame = self.capturer.capture()
        if frame is not None:
            print("Extracting text with Gemini...")
            text = self.vision.extract_text(frame)
            if text:
                print(f"Narrating: {text[:50]}...")
                self.audio.stream_and_play(text)
            else:
                print("No text found on screen.")
        else:
            print("Failed to capture screen.")

    def run(self):
        # System Tray Setup
        # Note: icon.png must exist in assets/
        try:
            image = Image.open("assets/icon.png")
        except FileNotFoundError:
            # Fallback to a simple generated image if icon.png is missing
            image = Image.new('RGB', (64, 64), color=(73, 109, 137))
            
        menu = pystray.Menu(pystray.MenuItem('Exit', self.on_exit))
        self.icon = pystray.Icon("ScreenBanter", image, "ScreenBanter Active", menu)

        # Register Hotkey (Ctrl + Alt + S)
        bindings = [["control + alt + s", None, self.on_trigger]]
        register_hotkeys(bindings)
        start_checking_hotkeys()

        print("ScreenBanter is active. Press Ctrl+Alt+S to narrate screen.")
        self.icon.run()

    def on_exit(self, icon):
        print("Exiting...")
        stop_checking_hotkeys()
        icon.stop()
        sys.exit(0)

if __name__ == "__main__":
    app = ScreenBanterApp()
    app.run()
