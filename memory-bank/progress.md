# Progress: ScreenBanter

**Current Status:** Scaffolded implementation phase. Initial skeletons for all core components have been created.

**What Works:**
- High-level architecture and component breakdown are defined.
- Project structure is scaffolded with implementation skeletons:
    - `server/tts_server.py` & `model_loader.py`: FastAPI backend for TTS.
    - `app/capture.py`: DXcam screen capture integration.
    - `app/vision.py`: Gemini 2.0 Flash Lite OCR integration.
    - `app/audio_client.py`: Asynchronous streaming audio playback.
    - `app/main.py`: System tray daemon and hotkey orchestration.
- `third_party/VibeVoice` repository is integrated for local model logic.

**What's Left to Build:**
- **Phase 1: Backend Latency:** Implement full logic in VibeVoice FastAPI server and verify CUDA performance.
- **Phase 2: Capture Speed:** Fine-tune DXcam capture loop and verify frame rates.
- **Phase 3: Cloud Bridge:** Finalize Gemini 2.0 Flash Lite prompt engineering and response handling.
- **Phase 4: Async Audio:** Refine the audio client buffer management to ensure smooth playback without jitter.
- **Phase 5: Packaging:** Configure Nuitka build script for standalone executable generation.

**Known Issues / Challenges (from README):**
- Audio Client implementation for streaming chunks can be complex to ensure smooth playback.
- Achieving target latency (~1.1s total) requires careful optimization of each component.
- Windows 11 and CUDA GPU are hard requirements for optimal performance.

**Evolution of Project Decisions:**
- Initial decision to use DXcam and VibeVoice-0.5B for performance reasons.
- Decision to use FastAPI for streaming TTS to minimize perceived latency.
- Decision to use Nuitka for packaging for performance over PyInstaller.
