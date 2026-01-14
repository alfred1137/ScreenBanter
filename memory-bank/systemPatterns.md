# System Patterns: ScreenBanter

**System Architecture:**
```mermaid
flowchart TD
    User[User] -->|Ctrl+Alt+S| InstantTrigger[Instant Capture]
    User -->|F10| QueueTrigger[Queue Capture]
    User -->|F11| ProcessTrigger[Process Queue]
    
    InstantTrigger --> Capture[Screen Capture (DXcam)]
    QueueTrigger -->|Add to List| ImageQueue[Screenshot Queue]
    ProcessTrigger -->|Send List| VisionEngine
    
    Capture -->|Single Frame| VisionEngine[Vision Engine (Gemini 2.0 Flash Lite API)]
    ImageQueue -->|Batch Frames| VisionEngine
    
    VisionEngine -- Extracted Text --> LocalInferenceServer[Local Inference Server (FastAPI + VibeVoice-0.5B)]
    LocalInferenceServer -- Streaming Audio Chunks --> FrontendDaemon[Frontend Daemon (Audio Client)]
    FrontendDaemon -- Play Audio (PyAudio) --> User
    
    TrayMenu[Tray Menu] -->|Open| SettingsGUI[Settings GUI (CustomTkinter)]
    SettingsGUI <-->|Read/Write| SettingsManager[Settings Manager]
    SettingsManager -.->|Apply| FrontendDaemon
    SettingsManager -.->|Config| LocalInferenceServer
```

**Key Technical Decisions:**
- **Modern Desktop GUI:** `CustomTkinter` will be used for the Settings window to provide a native, themed (Light/Dark mode) experience that matches Windows 11 aesthetics.
- **Settings Persistence:** A `settings.json` file in the application root will store all user preferences, managed by a centralized `SettingsManager` class.
- **Dynamic Hardware Discovery:**
    - **Voices:** The TTS server will dynamically scan for `.pt` files in the VibeVoice directory and expose them via a `/config` endpoint.
    - **Audio Devices:** `PyAudio` will be used to query and list physical output devices for user selection.
- **Capture Logic Extensions:**
    - **Active Window:** Uses `pygetwindow` or native Win32 APIs to find the foreground window's bounding box.
    - **Region Selection:** Implemented via a transparent, top-level overlay window for coordinate selection.

**Design Patterns in Use:**
- **Client-Server Architecture:** Decoupled Frontend Daemon and Inference Server allows for independent restarting and potential remote deployment.
- **Streaming Pattern:** Audio chunks are yielded immediately upon generation, reducing time-to-first-byte.
- **Producer-Consumer:** The `AudioClient` uses a thread-safe queue to buffer incoming audio chunks. It includes a pre-buffering stage where playback is delayed until a threshold (default 2.0s) is met to ensure continuity under load.

**Component Relationships:**

- **`app/main.py`:** The central orchestrator. Initializes the system tray, registers hotkeys from settings, manages the screenshot queue, and controls the server process lifecycle.

- **`app/settings.py`:** Contains `SettingsManager`, which handles `settings.json` persistence and provides a centralized API for other components to access configuration.

- **`app/settings_window.py`:** A `CustomTkinter`-based GUI for user configuration, including dynamic voice fetching from the server.

- **`app/region_selector.py`:** A `tkinter`-based transparent overlay for interactive capture area selection.

- **`app/capture.py`:** Wraps `DXcam` for high-speed screen and region grabbing.

- **`app/vision.py`:** Handles interaction with the Gemini API, supporting both single-image and multi-image payloads.

- **`app/audio_client.py`:** A threaded client that handles the persistent connection to the TTS server and smooth audio playback via `PyAudio`.

- **`server/tts_server.py`:** FastAPI entry point. Includes a warmup routine to eliminate cold-start latency.

- **`server/model_loader.py`:** Handles loading VibeVoice, managing CUDA devices, and dynamic discovery of voice presets (`.pt` files).
