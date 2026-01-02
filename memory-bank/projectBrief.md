# Project Brief: ScreenBanter

**Objective:** To create a real-time desktop narration tool that leverages Google's Gemini Vision for OCR and Microsoft's VibeVoice-0.5B for high-performance Text-to-Speech (TTS). The goal is to provide instantaneous audio narration of on-screen text, activated by a user hotkey.

**Core Components:**
1. **Frontend Daemon:** A system tray application responsible for screen capture, OCR integration, and audio playback orchestration.
2. **Local Inference Server:** A FastAPI application hosting the VibeVoice TTS model for streaming audio generation.

**Key Performance Target:** Achieve an end-to-end latency of approximately **1.1 seconds** from hotkey press to audible speech.
