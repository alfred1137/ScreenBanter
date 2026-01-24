# Active Context: ScreenBanter

**Current Work Focus:** Implementing Cloud TTS option via Gemini API and preparing v0.1.0 release.

**Recent Changes:**
- **Build System Refactor (v0.3.0)**:
    - **Deprecated "Full" Build**: Removed monolithic build logic to resolve CI memory limits (C1002) and eliminate LFS bandwidth costs.
    - **Lite-Only Artifact**: `build_release.py` now exclusively produces the lightweight client (~100MB) with Cloud TTS support.
    - **Workflow Simplification**: Removed matrix strategy from GitHub Actions, streamlining the release process to a single job.
- **Build System Stabilization (v0.2.x)**:
    - **CI Failure Resolution**: Replaced Linux-centric swap space actions with a native PowerShell script to manage the Windows Pagefile (12GB) on GitHub Actions runners.
    - **C1002 Heap Error Fix**: Implemented Nuitka's `--low-memory` flag in `build_release.py` to prevent MSVC compiler heap exhaustion during large file compilation.
    - **Code Cleanup**: Resolved `IndentationError` and logic issues in `build_release.py`.
    - **Dynamic Artifacts**: Updated `build.yml` to use release tags for dynamic zip and artifact naming.
- **Cloud TTS Support (2026-01-20)**:
    - Fully implemented Gemini 2.5 Flash Preview TTS with 30+ voice options.
    - Fixed `AttributeError` in Gemini response parsing and added WAV header stripping for clean PCM playback.
    - Serialized narration in `AudioClient` with a thread lock to prevent overlapping speech.
- **Gemini TTS Rotation Strategy (2026-01-22)**:
    - Implemented `KeyAndModelManager` in `app/tts_manager.py` for resilient API usage.
    - Added support for multiple API keys via `GEMINI_KEYS` environment variable.
    - Implemented a layered rotation strategy:
        1. **Model Rotation**: Retries with alternative models (e.g., `gemini-2.5-flash-native-audio-preview-12-2025`) on generic failures.
        2. **Key Rotation**: Immediately rotates to the next API key on 401/Invalid Key errors or when all models for a key have failed.
    - Updated `.env.example` with placeholders for multiple keys.
    - Verified with both simulated failure tests and real-world API validation.
- **Lite vs Full Packaging (2026-01-20)**:
    - Moved `uvicorn`, `fastapi`, `torch`, and other heavy ML deps to `optional-dependencies` in `pyproject.toml`.
    - Updated `build_release.py` to support `--lite` and `--full` (default) builds.
    - Updated `app/settings.py` to check for `fastapi` and `uvicorn` before allowing local TTS server startup.
    - **CI Optimization**: Updated GitHub Actions to use a matrix strategy (separate runners for Lite and Full) and increased the Windows pagefile (12GB) to prevent the "lost communication" (OOM) error during Nuitka compilation.
    - This allows for a "Lite" distribution (~100MB) for cloud-only users and a "Full" distribution (~5GB+) for local TTS users.
- **Full Workflow Verification (2026-01-20)**: Successfully tested HUD status updates, 4-bit quantized inference, region-specific screen capture, and Gemini OCR in a single session.
- **Versioning Alignment**: Decided to version the current release as `v0.1.0` to match `pyproject.toml` and reset the baseline for public availability.
- **Build Fix**:
    - Modified `build_release.py` to set `--jobs=1` for Nuitka. This limits compilation parallelism to prevent the "out of heap space" (C1002) error on memory-constrained GitHub Actions runners. Verified as stable.
- **Performance Mode Implementation**:
    - Added "Performance Mode" toggle in Settings GUI.
    - Integrated `bitsandbytes` 4-bit quantization support via `LOAD_IN_4BIT` environment variable injection.
    - Implemented server-side process prioritization (High Priority).
- **Banter HUD Implementation**:
    - Created `app/hud_window.py`: A frameless, topmost, semi-transparent overlay.
    - Integrated `WS_EX_NOACTIVATE` and `WS_EX_TOPMOST` styles.
    - Implemented "HUD / UI" settings tab to control:
        - `enabled`: Toggle HUD on/off.
        - `opacity`: Adjust transparency (0.1 - 1.0).
        - `steal_focus`: Optional force-focus behavior for priority.
    - Refactored `app/main.py` to use a dedicated GUI thread for the HUD, which now manages the Settings window as a Toplevel.
    - Wired HUD to display real-time OCR status ("Scanning", "Thinking", "Speaking") and extracted text.

## Current Focus
- **Decoupling Local TTS**: Shifting from a monolithic "Full" build to a "Bring Your Own Engine" model to bypass GitHub LFS limits and reduce distribution size.
- **Documentation**: Finalizing instructions for the new modular setup.

## Next Steps
- [x] **Code**: Remove "Full" build logic from `build_release.py` and GitHub Actions.
- [ ] **Feature**: Add `local_tts_path` setting and detection logic to `app/settings.py` and `app/main.py`.
- [ ] **Feature**: Implement `ExternalServerManager` to launch the TTS server from a user-provided path.
- [ ] **Docs**: Create `docs/setup_local_tts.md` guide for users to set up the VibeVoice environment manually.
- [ ] **Release**: Tag `v0.3.0` with the new architecture.

**Active Decisions and Considerations:**
- **Model Selection**: 
    - **OCR Engine**: `gemini-flash-lite-latest` (Gemini 2.5 Flash Lite) selected for high-speed, cost-effective multimodal extraction.
    - **Cloud TTS Engine**: `gemini-2.5-flash-preview-tts` (Native Speech) selected for its natural performance and 30 unique voice styles (Zephyr, Puck, Kore, etc.).
- **Release Versioning**: Standardizing on `v0.1.0` for the initial public launch to reflect "Beta" status while acknowledging feature completeness.
- **GUI Architecture**: Shifted from a transient Settings window to a persistent, hidden HUD root window. The HUD and Settings are now managed within a single Tkinter loop running in a dedicated thread. This ensures responsiveness and allows the HUD to stay active without blocking the system tray icon logic.
- **Quantization Strategy**: Adopting 4-bit quantization (via `bitsandbytes`) to drastically reduce VRAM usage (<500MB), preventing contention with VRAM-heavy games.
- **Priority Boosting**: Using OS-level priority boosts to prevent the Windows Scheduler from throttling the background TTS process during full-screen gaming.
- **Portable Folder vs. Onefile**: Decided to stick with a portable folder (standalone) zipped into an archive. This avoids the massive startup delay (20s+) associated with extracting a 2GB `onefile` executable containing `torch`.