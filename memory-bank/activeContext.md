# Active Context: ScreenBanter

**Current Work Focus:** Transitioning from scaffolding to functional implementation and environment verification.

**Recent Changes:**
- Project infrastructure and documentation review completed.
- Initial implementation skeletons created for all core components:
    - `app/main.py`: Orchestrator and tray app.
    - `app/capture.py`: DXcam screen capture.
    - `app/vision.py`: Gemini OCR integration.
    - `app/audio_client.py`: Async audio playback.
    - `server/tts_server.py` & `model_loader.py`: FastAPI TTS backend.
- Identified `third_party/VibeVoice` as the local repository for model logic.
- Updated Memory Bank to reflect scaffolded state.

**Next Steps:**
1. **Environment Verification:** User needs to install Microsoft Visual C++ Build Tools to resolve native dependency issues for `pyaudio` and `pystray`.
2. **Backend Validation:** Run and test the `server/tts_server.py` with the VibeVoice model to confirm CUDA acceleration and streaming performance.
3. **Capture & Vision Loop:** Test the `DXcam` and Gemini integration to verify OCR accuracy and latency.
4. **Asset Creation:** Add a placeholder `assets/icon.png` to satisfy application requirements.

**Active Decisions and Considerations:**
- **Native Dependencies:** `pyaudio` and `pystray` are currently the main blockers for a full `uv sync`.
- **Latency Budget:** Every component must be profiled to ensure we stay within the ~1.1s total end-to-end target.
- **VibeVoice Integration:** The code in `server/` assumes `vibevoice` package is available (either installed or in path).

**Learnings and Project Insights:**
- The project documentation was robust enough to allow immediate scaffolding of all major components.
- The use of `third_party/VibeVoice` suggests a modular approach to model integration, allowing for local improvements to the TTS logic.
