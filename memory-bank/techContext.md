# Technical Context: ScreenBanter

**Technologies Used:**
- **Python:** 3.10+ (Required for compatibility with certain ML libraries).
- **Google Gemini 2.0 Flash Lite API:** For high-speed, multi-modal OCR.
- **Microsoft VibeVoice-0.5B:** Local TTS model, running on `torch` with CUDA acceleration.
- **FastAPI/Uvicorn:** Backend server infrastructure.
- **DXcam:** Windows-specific high-speed screen capture.
- **PyAudio:** Low-level audio playback.
- **pystray:** System tray integration.
- **CustomTkinter:** Modern GUI for the settings window.
- **tkinter (Toplevel):** Transparent overlay for region selection.
- **global_hotkeys:** Global keyboard shortcuts with dynamic rebinding support.
- **uv:** Ultra-fast Python package and project manager.

**Development Environment:**
- **Package Management:** `uv` is used exclusively.
- **GPU:** NVIDIA GPU with CUDA 12.1 support is highly recommended.
- **OS:** Windows 10/11 (Strict requirement due to `DXcam` and `pystray` behavior).

**Key Dependencies & Constraints:**
- **Transformers:** Pinned to `4.51.3` to ensure compatibility with VibeVoice's specific internal logic.
- **PyTorch:** Must be the CUDA-enabled version.
- **CustomTkinter:** Used for a themed (Light/Dark mode) settings interface.
- **Native Build Tools:** `PyAudio` and `Pystray` often require Microsoft Visual C++ Build Tools during installation.

**Tool Usage Patterns:**
- **Run App:** `uv run python -m app.main`
- **Run Server Mode:** `uv run python -m app.main --server` (Used for packaged bundles)
- **Run Server (Debug):** `uv run uvicorn server.tts_server:app --port 8000`
- **Dependency Sync:** `uv sync`

**Project Structure:**
- The project is logically split into a **Frontend Daemon** (`app/`) and an **Inference Server** (`server/`).
- **Settings Management:** `app/settings.py` provides a centralized `SettingsManager` for `settings.json`.
- **GUI Components:** `app/settings_window.py` (Main GUI) and `app/region_selector.py` (Region selection tool).
- **Inference Adaptation:** `server/model_loader.py` adapts VibeVoice for library-style usage with dynamic voice discovery and warmup routines.