# Active Context: ScreenBanter

**Current Work Focus:** Verified TTS streaming with GPU acceleration (RTX 3060 Ti) and official VibeVoice logic.

**Recent Changes:**
- **Forced CUDA 12.1 Install**: Successfully installed `torch==2.5.1+cu121` and verified CUDA detection.
- **Dependency Alignment**: Downgraded `transformers` to `4.51.3` to match the official VibeVoice developer environment, resolving compatibility issues.
- **Model Loader Refactor**: Rewrote `server/model_loader.py` to achieve full parity with the official VibeVoice `StreamingTTSService`.
- **TTS Validation**: Successfully tested `server/tts_server.py` on `localhost:8000`, confirming real-time audio streaming.
- **Assets**: Added placeholder `assets/icon.png`.

**Next Steps:**
1.  **Vision Validation**: Run `test_vision.py` to verify Gemini API connectivity and OCR functionality.
2.  **Integrated Loop Test**: Execute a full "Capture -> Vision -> TTS" test to measure end-to-end latency.
3.  **App Launch**: Attempt to run the full `app/main.py` application.
4.  **Cleanup**: Remove temporary test scripts (`check_cuda.py`, `test_tts_stream_v2.py`, `test_vision.py`).

**Active Decisions and Considerations:**
- **Environment Stability**: The current `uv` environment is pinned to specific versions that are known to work with VibeVoice.
- **Latency**: First chunk delivery takes ~6.7s on the first request; further profiling is needed to see if subsequent requests are faster due to caching.
- **Native Dependencies**: `pyaudio` and `pystray` issues remain bypassed but will be needed for the final app.

**Learnings and Project Insights:**
- VibeVoice is extremely sensitive to `transformers` versions; using the developer-tested `4.51.3` is mandatory for stability.
- `uv` requires explicit `--index-url` and `--force-reinstall` when switching from CPU-only to CUDA-enabled PyTorch builds on Windows.
- Parity with the official demo logic (noise scheduler, voice preset caching) is critical for receiving valid audio streams.
