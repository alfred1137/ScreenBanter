# Active Context: ScreenBanter

**Current Work Focus:** Settings GUI Implementation. We are building the user-facing configuration layer to allow customization of Hotkeys, Voices, and System behavior.

**Recent Changes:**
- **Feature Planning**: Defined the comprehensive Settings GUI feature set, including TTS configuration, Vision style, Capture modes, and Performance optimization.
- **Architectural Decision**: Selected `CustomTkinter` for the settings interface to provide a modern Windows 11 look and feel.
- **Stability Improvements**:
    - **Process Isolation**: Used `subprocess.CREATE_NEW_PROCESS_GROUP` on Windows to prevent `SIGINT` (Ctrl+C) propagation from killing the background TTS server.
    - **Robust Startup**: Switched to `sys.executable` to launch the server, preventing `uv` environment conflicts.
    - **Persistent Logging**: Redirected server stdout/stderr to `logs/` files for post-mortem debugging.
    - Increased TTS client timeout to 45s.
    - Added comprehensive logging.
    - Refactored `app/main.py` to detect existing server instances.
    - Threaded startup sound.
- **Visual Branding**:
    - Replaced generic tray icon with custom `assets/icon.svg`.
    - Generated high-quality 64x64 PNG for system compatibility.
    - Integrated icon into `README.md` and configured it for the standalone executable in `build_release.py`.
- **Feature Completion**:
    - Multi-screenshot workflow (F10/F11).
    - Audio feedback and OCR logging.

**Next Steps:**
1.  **Settings Persistence (`app/settings.py`)**: Implement `SettingsManager` to handle `settings.json` load/save with default configurations (Hotkeys, Audio, System).
2.  **Server API Update (`server/tts_server.py`)**:
    *   Expose `GET /v1/voices` to list available voice presets.
    *   Update `TTSRequest` to accept `voice_key`.
    *   Update logic to pass `voice_key` to VibeVoice.
3.  **Application Integration**: Update `app/main.py` and `app/audio_client.py` to utilize dynamic settings.
4.  **Settings GUI (`app/settings_window.py`)**: Build the `CustomTkinter` interface for user interaction.
5.  **Packaging (Nuitka)**: Execute `build_release.py` to create the standalone distribution.

**Active Decisions and Considerations:**
- **Priority Shift: Settings vs. Packaging**: We have decided to prioritize the implementation of the Settings GUI over final standalone packaging. This ensures that the first distributed version is user-customizable (voices, hotkeys, audio devices) and that all dependencies (e.g., `customtkinter`) are captured during the final build process.
- **Windows Process Management**: On Windows, background processes spawned by a console application inherit the console. A `Ctrl+C` event is sent to all processes in the console group. We strictly use `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP` to isolate the TTS server, ensuring it survives interruptions or signals intended only for the CLI.
- **Server Warmup**: Implemented a `@app.on_event("startup")` handler in FastAPI. This forces the heavy VRAM loading and JIT compilation to occur *before* the server accepts requests. This solves the client-side timeout and "audio cutoff" issues definitively.
- **Asynchronous Startup**: The UI thread remains responsive while the server warms up in the background.
- **Multiprocessing in Frozen Apps**: The `--server` flag strategy allows the compiled `.exe` to act as both client and server.

**Learnings and Project Insights:**
- **Model Latency**: "Lazy loading" is bad for user experience in real-time apps. It's better to make the user wait during a clear "Loading..." phase than to have the first interaction fail or lag.
- **FastAPI Startup**: Startup events are blocking. This is useful for us as it ensures the `/health` endpoint only returns 200 when the model is *actually* ready to infer.

**Learnings and Project Insights:**
- **GUI Threads**: Even simple tray icons require careful thread management. Long-running startup tasks (like spawning a subprocess and polling it) should not block the UI initialization phase.
- **Model Warm-up**: Generative AI models have unavoidable cold-start latency; user feedback (sounds/notifications) is more important than raw speed for the initial interaction.