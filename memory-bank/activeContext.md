# Active Context: ScreenBanter

**Current Work Focus:** Fixing CI build failure for v1.1.0 release.

**Recent Changes:**
- **Build Fix**:
    - Modified `build_release.py` to set `--jobs=1` for Nuitka. This limits compilation parallelism to prevent the "out of heap space" (C1002) error on memory-constrained GitHub Actions runners.
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

**Next Steps:**
1.  **Release**: Tag `v1.1.0` and trigger the build workflow.
2.  **HUD Refinement**: Add playback controls (Stop/Skip) to the HUD if needed.

**Active Decisions and Considerations:**
- **GUI Architecture**: Shifted from a transient Settings window to a persistent, hidden HUD root window. The HUD and Settings are now managed within a single Tkinter loop running in a dedicated thread. This ensures responsiveness and allows the HUD to stay active without blocking the system tray icon logic.
- **Quantization Strategy**: Adopting 4-bit quantization (via `bitsandbytes`) to drastically reduce VRAM usage (<500MB), preventing contention with VRAM-heavy games.
- **Priority Boosting**: Using OS-level priority boosts to prevent the Windows Scheduler from throttling the background TTS process during full-screen gaming.
- **Portable Folder vs. Onefile**: Decided to stick with a portable folder (standalone) zipped into an archive. This avoids the massive startup delay (20s+) associated with extracting a 2GB `onefile` executable containing `torch`.