import os
import sys
import time
import requests
from PIL import Image
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.settings import settings_manager
from app.vision import VisionEngine
from app.audio_client import AudioClient

def test_integration():
    print("--- 1. Testing SettingsManager ---")
    voice = settings_manager.get_audio_config().get("voice_key")
    print(f"Default voice from settings: {voice}")
    if not voice:
        print("FAIL: No voice key found in settings.")
        return

    print("\n--- 2. Testing TTS Server Health & Voices ---")
    try:
        # Wait for server to warm up (it's heavy)
        print("Waiting for server to be ready (up to 60s)...")
        ready = False
        for _ in range(60):
            try:
                resp = requests.get("http://localhost:8000/health", timeout=1)
                if resp.status_code == 200:
                    ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not ready:
            print("FAIL: TTS Server not responding.")
            return

        resp = requests.get("http://localhost:8000/v1/voices")
        if resp.status_code == 200:
            voices = resp.json().get("voices", [])
            print(f"Available voices: {len(voices)}")
            if voice not in voices:
                print(f"WARNING: Current voice '{voice}' not in available voices list!")
        else:
            print(f"FAIL: Could not fetch voices. Status: {resp.status_code}")
            return
    except Exception as e:
        print(f"FAIL: Server test error: {e}")
        return

    print("\n--- 3. Testing VisionEngine (OCR) ---")
    vision = VisionEngine()
    sample_img = "assets/BBEventSample.webp"
    if not os.path.exists(sample_img):
        print(f"FAIL: Sample image not found at {sample_img}")
        return

    print(f"Processing {sample_img}...")
    try:
        pil_img = Image.open(sample_img).convert("RGB")
        img_array = np.array(pil_img)
        text = vision.extract_text(img_array)
    except Exception as e:
        print(f"FAIL: Error loading image or extracting text: {e}")
        return

    if text:
        print(f"OCR Success! Extracted {len(text)} characters.")
        print(f"Sample: {text[:100]}...")
    else:
        print("FAIL: OCR returned no text.")
        return

    print("\n--- 4. Testing AudioClient (TTS) ---")
    audio = AudioClient()
    # We won't actually "play" if there's no output device, but we can test the stream
    print(f"Requesting audio stream for extracted text using voice: {voice}")
    try:
        # We manually call the request part to verify the server handles the voice_key
        payload = {"text": text[:200], "voice_key": voice} # Use short text for test
        resp = requests.post("http://localhost:8000/v1/audio/stream", json=payload, stream=True, timeout=45)
        resp.raise_for_status()
        
        chunks = 0
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                chunks += 1
                if chunks > 5: # Just check if we get some data
                    break
        
        if chunks > 0:
            print(f"SUCCESS: Received audio chunks from server.")
        else:
            print("FAIL: No audio chunks received.")
    except Exception as e:
        print(f"FAIL: Audio stream error: {e}")

if __name__ == "__main__":
    test_integration()
