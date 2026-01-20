# System Patterns: ScreenBanter

**System Architecture:**
```mermaid
graph TD
    User[User] -->|Ctrl+Alt+S| InstantTrigger[Instant Capture]
    User -->|F10| QueueTrigger[Queue Capture]
    User -->|F11| ProcessTrigger[Process Queue]

    InstantTrigger --> Capture[Screen Capture (DXcam)]
    QueueTrigger -->|Add to List| ImageQueue[Screenshot Queue]
    ProcessTrigger -->|Send List| VisionEngine

    Capture -->|Single Frame| VisionEngine[Vision Engine (Gemini 2.5 Flash Lite API)]
    ImageQueue -->|Batch Frames| VisionEngine

    VisionEngine -- Extracted Text --> LocalInferenceServer[Local Inference Server (FastAPI + VibeVoice-0.5B - Full Version Only)]
    LocalInferenceServer -- Streaming Audio Chunks --> FrontendDaemon[Frontend Daemon (Audio Client)]
    FrontendDaemon -- Play Audio (PyAudio) --> User

    VisionEngine -- Extracted Text --> CloudTTS[Cloud TTS (Gemini API)]
    CloudTTS -- Audio Bytes --> FrontendDaemon

    TrayMenu[Tray Menu] -->|Open| HudManager[HUD Manager (Thread)]
    HudManager -->|Control| BanterHUD[Banter HUD (Persistent GUI)]
    BanterHUD -->|Open| SettingsGUI[Settings GUI (Toplevel)]
    SettingsGUI <-->|Read/Write| SettingsManager[Settings Manager]
    SettingsManager -.->|Env Vars| LocalInferenceServer
```
**Key Technical Decisions:**
- **GUI Architecture (Persistent HUD):**
    - The application uses a single persistent `customtkinter` loop running in a dedicated thread (`app/main.py` -> `init_hud`).
    - **Banter HUD (`app/hud_window.py`)** acts as the root controller. It is a frameless, topmost window that uses `pywin32` to apply `WS_EX_NOACTIVATE`, ensuring it provides feedback without stealing keyboard/mouse focus from games.
    - **Settings Window (`app/settings_window.py`)** is now a `CTkToplevel` child of the HUD, sharing the same event loop.
- **Performance Mode (Game Optimization):**
    - A "Master Toggle" in settings controls a suite of backend optimizations.
    - **TTS Provider Strategy:** The app supports switching between `local` (VibeVoice) and `gemini` (Cloud) TTS. This is handled by the `AudioClient`, which routes requests based on the `tts_provider` setting.
- **Configuration Injection:** The frontend daemon injects environment variables (e.g., `LOAD_IN_4BIT="true"`) when spawning the TTS server subprocess based on `settings.json`.
- **Cloud TTS Integration:** Uses the `google-genai` SDK's `generate_content` method with `AUDIO` modality. The resulting audio bytes are chunked and played via the same `AudioClient` worker as the local stream.    - **Quantization:** Uses `bitsandbytes` 4-bit quantization to reduce VRAM footprint from ~1.5GB to <500MB.
    - **Priority:** The server process sets itself to `HIGH_PRIORITY_CLASS` on Windows startup.
- **Modern Desktop GUI:** `CustomTkinter` provides a native, themed (Light/Dark mode) experience matching Windows 11 aesthetics.
- **Settings Persistence:** A `settings.json` file in the application root stores all user preferences, managed by a centralized `SettingsManager` class.
- **Dynamic Hardware Discovery:**
    - **Voices:** The TTS server dynamically scans for `.pt` files in the VibeVoice directory and exposes them via a `/config` endpoint.

**Design Patterns in Use:**
- **Client-Server Architecture:** Decoupled Frontend Daemon and Inference Server allows for independent restarting and potential remote deployment.
- **Streaming Pattern:** Audio chunks are yielded immediately upon generation, reducing time-to-first-byte.
- **Producer-Consumer:** The `AudioClient` uses a thread-safe queue to buffer incoming audio chunks. It includes a pre-buffering stage where playback is delayed until a threshold (default 2.0s) is met to ensure continuity under load.

**Component Relationships:**

- **`app/main.py`:** The central orchestrator. Initializes the system tray, registers hotkeys, manages the screenshot queue, and launches the HUD thread and Server subprocess.

- **`app/hud_window.py`:** The main visual interface during operation. Manages the GUI event loop and displays real-time status.

- **`app/settings.py`:** Contains `SettingsManager`, handling `settings.json` persistence.

- **`app/settings_window.py`:** A `CTkToplevel` GUI for configuration.

- **`app/region_selector.py`:** A transparent overlay for interactive capture area selection.

- **`app/capture.py`:** Wraps `DXcam` for high-speed screen and region grabbing.

- **`app/vision.py`:** Handles interaction with the Gemini API.

- **`app/audio_client.py`:** Handles audio playback via `PyAudio`.

- **`server/tts_server.py`:** FastAPI entry point. Includes a warmup routine and priority setting.

- **`server/model_loader.py`:** Handles loading VibeVoice with optional quantization.