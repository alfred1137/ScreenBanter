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
    
    if not os.getenv("GEMINI_KEYS"):
        print("SKIP: GEMINI_KEYS not found in environment. Please set it to a comma-separated list of keys.")
        return

    print("--- Testing Gemini Cloud TTS with Key and Model Rotation ---")
    
    # Configure settings for cloud TTS
    settings_manager.set("audio", "tts_provider", "gemini")
    settings_manager.set("audio", "cloud_voice", "Puck") # Or any other valid voice
    
    client = AudioClient()
    
    test_text = "This is a test of the Screen Banter Cloud TTS integration using the new Key and Model Manager. If this works, the resilient rotation strategy is likely functioning correctly."
    print(f"Requesting speech for: '{test_text}'")
    
    try:
        # The client will now internally use the tts_manager for keys and models
        client.stream_and_play(test_text)
        print("\nCloud TTS test completed successfully.")
        print("NOTE: This test does not simulate API failures to test rotation.")
        print("To fully test, provide invalid keys in the GEMINI_KEYS list before a valid one.")
    except Exception as e:
        print(f"Cloud TTS test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cloud_tts()
