# Progress: ScreenBanter

**Overall Status:** TTS verified on GPU with official VibeVoice logic; environment issues resolved.

**Completed:**
- `pyproject.toml`: Added detailed VibeVoice dependencies and pinned `transformers==4.51.3`.
- **Environment Integration**: Successfully performed a forced reinstall of CUDA 12.1-enabled PyTorch.
- **CUDA Verification**: Confirmed RTX 3060 Ti visibility via standalone test.
- `server/model_loader.py`: Completely refactored to achieve parity with the official VibeVoice `StreamingTTSService`, including noise scheduler and voice preset caching.
- `server/tts_server.py`: Verified functional on `localhost:8000` with real-time streaming response.
- **Assets**: Created placeholder `assets/icon.png` for system tray.

**Remaining:**
- Test Gemini API connectivity via `test_vision.py` and `app/vision.py`.
- Execute integrated loop test (Capture -> Vision -> TTS).
- Address native dependency issues for `pyaudio` and `pystray` (build tools requirement).
- Finalize application UI/Tray integration.

**Known Issues:**
- `FlashAttention2` is not installed; the model falls back to `SDPA` (this is expected and currently functional).
- First request latency is ~6.7s for the first chunk; subsequent requests should be profiled.
- Native libraries (`pyaudio`) need manual installation or specific environment fixes on Windows.

**Decision History:**
- *Interruption Recovery*: Re-aligned with the official demo notebooks and scripts after initial integration failures.
- *Dependency Pinning*: Chose to downgrade `transformers` to `4.51.3` rather than monkeypatching the newer version further.
- *Localhost over 0.0.0.0*: Switched server binding to `127.0.0.1` for improved reliability in local dev.
