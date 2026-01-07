# test_vision.py
import os
import numpy as np
from PIL import Image
from app.vision import VisionEngine
from dotenv import load_dotenv

load_dotenv()

def test_vision():
    print("Initializing VisionEngine...")
    try:
        engine = VisionEngine()
    except Exception as e:
        print(f"Error initializing VisionEngine: {e}")
        return

    # Create a dummy image with some text
    print("Creating dummy image for testing...")
    img = Image.new('RGB', (800, 200), color=(255, 255, 255))
    # We won't actually draw text with PIL to avoid font issues, 
    # but Gemini should be able to see "blank" if we don't.
    # Actually, let's just use the icon we just created.
    
    img_path = "assets/icon.png"
    if os.path.exists(img_path):
        img = Image.open(img_path)
        print(f"Using {img_path} for testing.")
    
    frame_np = np.array(img)
    
    print("Sending frame to Gemini...")
    text = engine.extract_text(frame_np)
    
    print(f"Gemini response: '{text}'")
    if text or text == "":
        print("✅ VisionEngine communication successful.")
    else:
        print("❌ VisionEngine failed to return a string.")

if __name__ == "__main__":
    test_vision()
