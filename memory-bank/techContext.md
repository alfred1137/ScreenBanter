# Technical Context: ScreenBanter

**Technologies Used:**
- **Python:** Primary programming language.
- **Google Gemini 2.0 Flash Lite API:** For high-speed and accurate Optical Character Recognition (OCR).
- **Microsoft VibeVoice-0.5B:** Local Text-to-Speech (TTS) model for real-time audio generation.
    - Integrated as a local submodule/repository in `third_party/VibeVoice`.
- **FastAPI:** Python web framework for building the local inference server for VibeVoice.
- **DXcam:** High-performance screen capture library for Windows 11.
- **PyAudio:** Python library for playing and recording audio, used for streaming audio playback.
- **pystray:** Python library for creating system tray applications.
- **global_hotkeys:** Python library for registering and handling global hotkeys.
- **Nuitka:** Python compiler for packaging the application into a standalone executable (`.exe`).
- **uvicorn:** ASGI server for running FastAPI applications.
- **torch:** PyTorch library for machine learning, used by VibeVoice.
- **numpy:** Python library for numerical operations, likely used in conjunction with DXcam for image processing.
- **PIL (Pillow):** Python imaging library, used for image manipulation (e.g., loading icons).
- **requests:** Python library for making HTTP requests (e.g., to the local TTS server).

**Development Setup:**
- Python 3.8+ recommended.
- GPU (CUDA compatible) for VibeVoice model inference.
- `.env` file for API keys (e.g., `GEMINI_KEY`) and local paths.

**Technical Constraints:**
- **Windows 11 Specific:** `DXcam` is optimized for Windows 11, limiting cross-platform compatibility without alternative capture methods.
- **GPU Requirement:** VibeVoice performance is highly dependent on CUDA-enabled GPU for achieving low latency.
- **API Key Dependency:** Google Gemini API requires an API key for OCR functionality.
- **Native Dependencies:** `PyAudio` and `Pystray` require Microsoft Visual C++ Build Tools for installation on Windows.

**Dependencies (High-Level):**
- `google-generativeai`
- `torch`
- `uvicorn`
- `fastapi`
- `dxcam`
- `pyaudio`
- `pystray`
- `global_hotkeys`
- `Nuitka`
- `numpy`
- `Pillow`
- `requests`
- `python-dotenv` (for `.env` handling)

**Tool Usage Patterns:**
- `uv` for Python project management (venv, package installation, etc.)
- `uvicorn` for running the FastAPI server.
- `Nuitka` for final application packaging.
