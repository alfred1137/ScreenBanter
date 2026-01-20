# Active Context: ScreenBanter

**Current Work Focus:** Implementing Cloud TTS option via Gemini API and preparing v0.1.0 release.

**Recent Changes:**
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

**Planned Changes (Issue #15):**
- **Cloud TTS Support**:
    - Add `tts_provider` setting (Local vs. Gemini Cloud).
    - Implement Gemini TTS integration in `AudioClient` using `google-genai` SDK.
    - Allow skipping local TTS server startup if Gemini Cloud is selected.
    - Add cloud-specific settings: `cloud_model` and `cloud_voice`.

**Next Steps:**
1.  **Implement Cloud TTS**: Update settings, main app logic, and audio client.
2.  **Verification**: Test both local and cloud TTS modes.
3.  **Release**: Tag `v0.1.0` and trigger the build workflow.

**Active Decisions and Considerations:**
- **Release Versioning**: Standardizing on `v0.1.0` for the initial public launch to reflect "Beta" status while acknowledging feature completeness.
- **GUI Architecture**: Shifted from a transient Settings window to a persistent, hidden HUD root window. The HUD and Settings are now managed within a single Tkinter loop running in a dedicated thread. This ensures responsiveness and allows the HUD to stay active without blocking the system tray icon logic.
- **Quantization Strategy**: Adopting 4-bit quantization (via `bitsandbytes`) to drastically reduce VRAM usage (<500MB), preventing contention with VRAM-heavy games.
- **Priority Boosting**: Using OS-level priority boosts to prevent the Windows Scheduler from throttling the background TTS process during full-screen gaming.
- **Portable Folder vs. Onefile**: Decided to stick with a portable folder (standalone) zipped into an archive. This avoids the massive startup delay (20s+) associated with extracting a 2GB `onefile` executable containing `torch`.