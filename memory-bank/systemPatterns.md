# System Patterns: ScreenBanter

**System Architecture:**
```mermaid
flowchart TD
    User[User Hotkey: Ctrl+Alt+S] --> FrontendDaemon[Frontend Daemon (System Tray)]
    FrontendDaemon -- Screen Capture (DXcam) --> VisionEngine[Vision Engine (Gemini 2.0 Flash Lite API)]
    VisionEngine -- Extracted Text --> LocalInferenceServer[Local Inference Server (FastAPI + VibeVoice-0.5B)]
    LocalInferenceServer -- Streaming Audio Chunks --> FrontendDaemon
    FrontendDaemon -- Play Audio (PyAudio) --> User
```

**Key Technical Decisions:**
- **High-Speed Screen Capture:** `DXcam` for Windows 11 due to its 10x performance advantage over standard screenshot tools (5-10ms capture time).
- **Efficient OCR:** Google Gemini 2.0 Flash Lite API for precise and fast text extraction from screen captures.
- **Real-time TTS:** Microsoft VibeVoice-0.5B model, wrapped in FastAPI, to provide streaming audio generation, enabling playback before the full sentence is synthesized. The VibeVoice model itself is managed locally via the `third_party/VibeVoice` repository, allowing for direct code integration and optimization.
- **Async Audio Playback:** `PyAudio` to handle streaming audio chunks from the local server, ensuring smooth, non-blocking playback.
- **Background Operation:** `pystray` for a system tray application to run the Frontend Daemon discreetly.
- **Application Bundling:** `Nuitka` for packaging into a single `.exe` for optimal performance and startup on boot.

**Design Patterns in Use:**
- **Client-Server Architecture:** Clear separation between the Frontend Daemon (client) and the Local Inference Server (server).
- **Streaming Pattern:** Used for audio delivery from the TTS server to the client, improving perceived latency.
- **Observer Pattern (Implicit):** The hotkey listener acts as an observer, triggering the narration process.

**Component Relationships:**
- **`app/main.py` (Orchestrator):** Coordinates screen capture, OCR, TTS request, and audio playback. Manages the system tray icon and hotkey.
- **`app/capture.py`:** Provides the `DXcam` interface for fast screen grabbing.
- **`app/vision.py`:** Handles interaction with the Gemini API for text extraction.
- **`app/audio_client.py`:** Manages the streaming audio reception and playback using `PyAudio`.
- **`server/tts_server.py`:** Exposes a FastAPI endpoint for text-to-speech requests and streams audio responses.
- **`server/model_loader.py`:** Responsible for loading the VibeVoice model and CUDA setup.
