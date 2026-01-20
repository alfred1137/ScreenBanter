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
- **PyTorch:** Must be the CUDA-enabled version (Full version only).
- **Lite vs Full Split:**
    - **Lite Version:** Cloud-only (Gemini TTS). Excludes `torch`, `transformers`, `fastapi`, `uvicorn`, and local models. Significantly smaller package size.
    - **Full Version:** Includes Local TTS (VibeVoice) support with all heavy ML dependencies and model weights.

**Tool Usage Patterns:**
- **Run App:** `uv run python -m app.main`
- **Install for Lite:** `uv sync` (default)
- **Install for Full:** `uv sync --extra local-tts`
- **Build Lite:** `python build_release.py --lite`
- **Build Full:** `python build_release.py`
- **Run Server Mode:** `uv run python -m app.main --server` (Used for packaged bundles, Full only)
- **Run Server (Debug):** `uv run uvicorn server.tts_server:app --port 8000` (Full only)

**Project Structure:**
- The project is logically split into a **Frontend Daemon** (`app/`) and an **Inference Server** (`server/`).
- **Settings Management:** `app/settings.py` provides a centralized `SettingsManager` for `settings.json`.
- **GUI Components:** `app/settings_window.py` (Main GUI) and `app/region_selector.py` (Region selection tool).
- **Inference Adaptation:** `server/model_loader.py` adapts VibeVoice for library-style usage with dynamic voice discovery and warmup routines.