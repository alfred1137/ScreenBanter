# Active Context: ScreenBanter

**Current Work Focus:** Finalizing manual verification and preparing for standalone packaging. Core features including the Settings GUI and Region Capture are implemented and verified.

**Recent Changes:**
- **Thread-Safe UI Management**: Fixed `RuntimeError` by implementing a thread-safe window lifecycle flag for the Settings GUI, preventing cross-thread Tkinter access.
- **Configurable Performance**: Added UI controls for "Process Priority" and "Playback Buffer" (0.5s - 10.0s) to the Settings GUI.
- **Process Priority Fix**: Refined `ctypes` implementation for Windows priority management with explicit type definitions.
- **Audio Optimization**: Increased adaptive buffer to 4.0s (now user-configurable) and set application process priority to `ABOVE_NORMAL` by default.
- **Hotkey Responsiveness**: Refactored `on_process_queue` to run OCR and TTS in a background thread.

**Next Steps:**
1.  **Packaging (Nuitka)**: Execute and verify `build_release.py` to create a standalone executable.
2.  **Release Preparation**: Final documentation review and asset check.

**Active Decisions and Considerations:**
- **Threading Model**: The application uses a strict "UI vs Worker" split. The System Tray and Settings GUI are managed carefully to avoid Tkinter's single-thread affinity issues. All heavy processing (Vision, TTS, Playback) is offloaded to daemon threads.
- **Adaptive Buffering**: We use a "Play-when-ready" strategy where audio starts after either the buffer fills or the stream ends. This provides the best balance between stability and latency.
- **Background Performance**: By default, we use `ABOVE_NORMAL` priority to ensure the audio playback thread is not starved by other intensive background or foreground applications.