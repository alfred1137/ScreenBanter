# app/tts_manager.py
import os
import threading

class KeyAndModelManager:
    """
    Manages a pool of Gemini API keys and a fixed list of TTS models.

    This class implements a layered rotation strategy:
    1. Inner Loop (Models): Rotates through available models for the current key.
    2. Outer Loop (Keys): Rotates through available keys when all models have failed for a key.
    """
    MODELS = ['gemini-2.5-flash-preview-tts', 'gemini-2.5-flash-native-audio-preview-12-2025']

    def __init__(self):
        self._lock = threading.Lock()
        self.api_keys = self._load_keys()
        self.key_index = 0
        self.model_index = 0

    def _load_keys(self):
        """Loads API keys from the GEMINI_KEYS environment variable."""
        keys_str = os.getenv("GEMINI_KEYS")
        if not keys_str:
            print("Warning: GEMINI_KEYS environment variable not set or empty.")
            return []
        keys = [key.strip() for key in keys_str.split(',') if key.strip()]
        if not keys:
            print("Warning: No valid API keys found in GEMINI_KEYS.")
        return keys

    def get_current(self):
        """Returns the current (key, model) pair."""
        with self._lock:
            if not self.api_keys:
                return None, None
            key = self.api_keys[self.key_index]
            model = self.MODELS[self.model_index]
            return key, model

    def advance_model(self):
        """
        Advances the model index. Returns True if a new model is available under the current key,
        False otherwise (indicating model rotation has looped).
        """
        with self._lock:
            self.model_index = (self.model_index + 1) % len(self.MODELS)
            return self.model_index != 0

    def advance_key(self):
        """
        Advances the key index and resets the model index. Returns True if a new key is available,
        False otherwise (indicating key rotation has looped).
        """
        with self._lock:
            self.key_index = (self.key_index + 1) % len(self.api_keys)
            self.model_index = 0 # Reset model index on key change
            return self.key_index != 0

    def has_keys(self):
        """Checks if any API keys are loaded."""
        return bool(self.api_keys)

# Global instance
tts_manager = KeyAndModelManager()
