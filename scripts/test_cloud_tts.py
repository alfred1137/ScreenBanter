# scripts/test_cloud_tts.py
import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.audio_client import AudioClient
from app.settings import settings_manager

def test_cloud_tts():
    load_dotenv()
    
    if not os.getenv("GEMINI_KEY"):
        print("SKIP: GEMINI_KEY not found in environment.")
        return

    print("--- Testing Gemini Cloud TTS ---")
    
    # Configure settings for cloud TTS
    settings_manager.set("audio", "tts_provider", "gemini")
    settings_manager.set("audio", "cloud_model", "gemini-2.5-flash-preview-tts")
    settings_manager.set("audio", "cloud_voice", "Puck")
    
    client = AudioClient()
    
    test_text = "This is a test of the Screen Banter Cloud T T S integration using Gemini."
    print(f"Requesting speech for: '{test_text}'")
    
    try:
        client.stream_and_play(test_text)
        print("Cloud TTS test completed successfully.")
    except Exception as e:
        print(f"Cloud TTS test failed: {e}")

if __name__ == "__main__":
    test_cloud_tts()
