import json
import os
from typing import Dict, Any

class SettingsManager:
    DEFAULT_SETTINGS = {
        "hotkeys": {
            "trigger": "control + alt + s",
            "queue": "f10",
            "process": "f11"
        },
        "audio": {
            "tts_provider": "local",
            "voice_key": "en-Davis_man",
            "volume": 1.0,
            "speed": 1.0,
            "buffer_seconds": 4.0,
            "playback_mode": "stream",
            "cloud_model": "gemini-2.5-flash-preview-tts",
            "cloud_voice": "Puck",
            "local_tts_path": ""
        },
        "capture": {
            "use_region": True,
            "region": None
        },
        "hud": {
            "enabled": True,
            "opacity": 0.9,
            "steal_focus": False
        },
        "system": {
            "minimize_to_tray": True,
            "play_startup_sound": True,
            "priority": "above_normal"
        },
        "performance_mode": {
            "enabled": False,
            "quantization": "4bit",
            "force_hud": False,
            "process_priority": "high"
        }
    }

    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Loads settings from file or returns defaults if file doesn't exist."""
        if not os.path.exists(self.settings_file):
            return self.DEFAULT_SETTINGS.copy()
        
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Deep merge with defaults to ensure all keys exist
                return self._merge_settings(self.DEFAULT_SETTINGS.copy(), loaded)
        except Exception as e:
            print(f"Error loading settings: {e}. Using defaults.")
            return self.DEFAULT_SETTINGS.copy()

    def _merge_settings(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively updates default settings with loaded values."""
        for key, value in loaded.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_settings(default[key], value)
            else:
                default[key] = value
        return default

    def save_settings(self):
        """Saves current settings to file."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            print("Settings saved successfully.")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, section: str, key: str) -> Any:
        """Retrieves a specific setting value."""
        return self.settings.get(section, {}).get(key)

    def set(self, section: str, key: str, value: Any):
        """Updates a specific setting value and saves immediately."""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save_settings()

    def get_hotkey(self, name: str) -> str:
        return self.get("hotkeys", name)
    
    def get_audio_config(self) -> Dict[str, Any]:
        return self.settings.get("audio", self.DEFAULT_SETTINGS["audio"])

    def is_local_tts_supported(self) -> bool:
        """
        Checks if the local TTS engine (VibeVoice) is supported.
        1. Checks if 'local_tts_path' points to a valid external engine.
        2. Fallback: Checks for local dependencies (torch, etc.) for dev/full builds.
        """
        # 1. External Engine Check
        local_path = self.get("audio", "local_tts_path")
        if local_path and os.path.exists(local_path):
            return True

        # 2. Internal/Dev Environment Check
        try:
            import torch
            import fastapi
            import uvicorn
            # Also check if the server code is actually present
            server_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server", "tts_server.py")
            return os.path.exists(server_path)
        except ImportError:
            return False

# Global instance
settings_manager = SettingsManager()
