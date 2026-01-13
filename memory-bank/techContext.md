# Technical Context: ScreenBanter

**Technologies Used:**
- **Python:** 3.10+ (Required for compatibility with certain ML libraries).
- **Google Gemini 2.0 Flash Lite API:** For high-speed, multi-modal OCR.
- **Microsoft VibeVoice-0.5B:** Local TTS model, running on `torch` with CUDA acceleration.
- **FastAPI/Uvicorn:** Backend server infrastructure.
- **DXcam:** Windows-specific high-speed screen capture.
- **PyAudio:** Low-level audio playback.
- **pystray:** System tray integration.
- **global_hotkeys:** Global keyboard shortcuts.
- **uv:** Ultra-fast Python package and project manager.

**Development Environment:**
- **Package Management:** `uv` is used exclusively.
- **GPU:** NVIDIA GPU with CUDA 12.1 support is highly recommended.
- **OS:** Windows 10/11 (Strict requirement due to `DXcam` and `pystray` behavior).

**Key Dependencies & Constraints:**
- **Transformers:** Pinned to `4.51.3` to ensure compatibility with VibeVoice's specific internal logic.
- **PyTorch:** Must be the CUDA-enabled version (`index-url` management handled via `uv` or manual pip args).
- **Native Build Tools:** `PyAudio` and `Pystray` often require Microsoft Visual C++ Build Tools during installation.

**Tool Usage Patterns:**
- **Run Client:** `uv run python -m app.main`
- **Run Server (Debug):** `uv run uvicorn server.tts_server:app --reload`
- **Dependency Sync:** `uv sync`

**Project Structure:**
- The project allows the server and client to run in the same environment but logically separated processes.
- `server/model_loader.py` contains the critical adaptation logic to make VibeVoice work as a library.