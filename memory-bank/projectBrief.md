# Project Brief: ScreenBanter

**Objective:** To create a real-time desktop narration tool that leverages Google's Gemini Vision for OCR and a choice of high-performance Text-to-Speech (TTS) engines: Microsoft's VibeVoice-0.5B (Local) or Google's Gemini 2.5 Flash Preview TTS (Cloud). The goal is to provide instantaneous audio narration of on-screen text, activated by a user hotkey.

**Key Requirements:**
1. **Screen Capture Daemon:** A background application (Windows tray) that listens for hotkeys and captures specific screen regions or full screens.
2. **Dual Inference Strategy:**
    - **Local Inference Server:** A FastAPI application hosting the VibeVoice TTS model for streaming audio generation without cloud dependencies.
    - **Cloud Inference:** Direct integration with Gemini API (`gemini-2.5-flash-preview-tts`) for high-quality audio generation with minimal local resource usage.
3. **Vision Processing:** Integration with Gemini Flash Lite for robust OCR and content intelligent merging.
4. **Real-time Performance:** Low-latency end-to-end pipeline (capture to audio start) under 1.5 seconds.
5. **HUD Overlay:** Non-intrusive status overlay and text preview.

**Core Components:**
1. **Frontend Daemon:** A system tray application responsible for screen capture, OCR integration, and audio playback orchestration.
2. **Local Inference Server:** A FastAPI application hosting the VibeVoice TTS model for streaming audio generation.

**Key Performance Target:** Achieve an end-to-end latency of approximately **1.1 seconds** from hotkey press to audible speech.
