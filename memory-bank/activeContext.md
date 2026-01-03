# Active Context: ScreenBanter

**Current Work Focus:** Completed VibeVoice TTS model integration and GPU acceleration.

**Recent Changes:**
- Implemented VibeVoice TTS model integration.
- Configured environment for GPU (CUDA) acceleration.
- Resolved various dependency and path issues for VibeVoice.

**Next Steps:**
1.  **Backend Validation:** Complete testing of the `server/tts_server.py` with the VibeVoice model to confirm streaming performance.
2.  **Capture & Vision Loop:** Test the `DXcam` and Gemini integration to verify OCR accuracy and latency.
3.  **Asset Creation:** Add a placeholder `assets/icon.png` to satisfy application requirements.
4.  **Cleanup**: Remove temporary files `check_cuda.py` and `test_tts_stream.py`.

**Active Decisions and Considerations:**
- **Native Dependencies:** Initial blocking `pyaudio` and `pystray` issues were bypassed by focusing on core TTS functionality. These will need to be addressed for full application functionality.
- **Latency Budget:** Further profiling is needed to ensure the entire pipeline (capture -> OCR -> TTS -> playback) stays within the ~1.1s total end-to-end target.
- **VibeVoice Integration Stability:** The current integration is functional, but robustness with varying inputs and edge cases needs further testing.

**Learnings and Project Insights:**
- `uv` environment management requires careful handling of editable installs and their dependencies, often necessitating manual `sys.path` modifications.
- PyTorch CUDA detection can be tricky and requires verifying both PyTorch installation with CUDA wheels and proper CUDA driver setup on the system.
- The iterative debugging process was crucial in identifying and resolving dependency chain issues and environment configuration.
