# Active Context: ScreenBanter

**Current Work Focus:** Finalizing manual verification and preparing for standalone packaging. Core features including the Settings GUI and Region Capture are implemented and verified.

**Recent Changes:**
- **Settings GUI**: Full implementation of configuration window using `CustomTkinter` with dynamic voice selection.
- **Region Capture**: Interactive selection tool using a transparent `tkinter` overlay, integrated with DXcam.
- **Settings Persistence**: Centralized `SettingsManager` for `settings.json` and dynamic hotkey rebinding.
- **Server Optimization**: Implemented model warmup to eliminate first-request latency.

**Next Steps:**
1.  **Packaging (Nuitka)**: Execute and verify `build_release.py` to create a standalone executable.
2.  **Release Preparation**: Final documentation review and asset check.

**Active Decisions and Considerations:**
- **Settings Persistence**: Used `settings.json` for simple, human-readable configuration that can be easily backed up or manually edited.
- **Dynamic Hotkeys**: While the GUI saves hotkeys, they currently require an application restart to re-register with the `global_hotkeys` engine to ensure clean state.
- **Warmup Trade-off**: The server takes ~10-15s longer to start due to pre-caching and JIT compilation, but this ensures the first user interaction is sub-second.