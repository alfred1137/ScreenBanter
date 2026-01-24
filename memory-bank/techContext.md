# Technical Context: ScreenBanter

**Technologies Used:**
- **Python:** 3.10+ (Required for compatibility with certain ML libraries).
- **Google Gemini 2.5 Flash Lite API (`gemini-flash-lite-latest`):** For high-speed, multi-modal OCR.
- **Google Gemini 2.5 Flash Preview TTS (`gemini-2.5-flash-preview-tts`):** For high-quality native cloud-based text-to-speech.
- **Microsoft VibeVoice-0.5B:** Local TTS model, running on `torch` with CUDA acceleration.

**Gemini Cloud TTS Voice Options:**
Supports 30 native voices configurable via `voice_name`:
- **Zephyr, Puck, Autonoe, Laomedeia** (Bright/Upbeat)
- **Kore, Orus, Erinome, Iapetus, Alnilam** (Firm/Clear)
- **Algieba, Despina, Achernar, Sulafat, Vindemiatrix** (Smooth/Soft/Warm)
- **Charon, Rasalgethi, Sadaltager, Schedar, Gacrux** (Informative/Mature)
- **Callirrhoe, Umbriel, Zubenelgenubi, Achird, Leda** (Easy-going/Friendly)
- **Fenrir, Aoede, Enceladus, Pulcherrima, Sadachbia** (Other styles)
- **google-genai:** Unified Python SDK for Gemini Vision and TTS.
- **bitsandbytes:** 8-bit/4-bit optimization for model quantization.
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
- **PyTorch:** Must be the CUDA-enabled version (Required for Local TTS Engine).
- **Deployment Models:**
    - **Lite Client (Standard):** The default distribution. Cloud-only dependencies. Excludes `torch`, `transformers`, `fastapi`, and model weights to keep the package small (~100MB).
    - **Local TTS (BYOE):** Local VibeVoice support is achieved via a "Bring Your Own Engine" model. Users configure a `local_tts_path` pointing to an external Python environment or executable hosting the server logic.

**Tool Usage Patterns:**
- **Run App:** `uv run python -m app.main`
- **Install for Lite (Cloud only):** `uv sync` (default)
- **Install for Local Dev:** `uv sync --extra local-tts`
- **Build Release:** `python build_release.py` (Produces Lite Client)
- **Run Server (Debug):** `uv run uvicorn server.tts_server:app --port 8000` (Requires `local-tts` extras)

**Project Structure:**
- The project is logically split into a **Frontend Daemon** (`app/`) and an **Inference Server** (`server/`).
- **Settings Management:** `app/settings.py` provides a centralized `SettingsManager` for `settings.json`.
- **GUI Components:** `app/settings_window.py` (Main GUI) and `app/region_selector.py` (Region selection tool).
- **Inference Adaptation:** `server/model_loader.py` adapts VibeVoice for library-style usage with dynamic voice discovery and warmup routines.