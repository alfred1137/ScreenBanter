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
```

**Key Technical Decisions:**
- **High-Speed Screen Capture:** `DXcam` for Windows 11 due to its 10x performance advantage (5-10ms).
- **Batch OCR:** Gemini 2.0 Flash Lite's ability to process multiple images in a single context window allows for coherent narration of multi-page content.
- **Real-time TTS:** Microsoft VibeVoice-0.5B model, managed by a custom `VibeVoiceManager` that ensures parity with official research code (caching, noise scheduling).
- **Streaming Audio:** `PyAudio` running in a dedicated daemon thread to prevent UI blocking and ensure smooth playback.
- **Robust Process Management:** The Frontend Daemon (`app/main.py`) manages the lifecycle of the Local Inference Server, checking for existing instances before spawning new ones.

**Design Patterns in Use:**
- **Client-Server Architecture:** Decoupled Frontend Daemon and Inference Server allows for independent restarting and potential remote deployment.
- **Streaming Pattern:** Audio chunks are yielded immediately upon generation, reducing time-to-first-byte.
- **Producer-Consumer:** The `AudioClient` uses a thread-safe queue to buffer incoming audio chunks for the playback worker.

**Component Relationships:**
- **`app/main.py`:** The central orchestrator. Initializes the system tray, registers hotkeys, manages the screenshot queue, and controls the server process.
- **`app/capture.py`:** Wraps `DXcam` for reliable screen grabbing.
- **`app/vision.py`:** Handles interaction with the Gemini API, supporting both single-image and multi-image payloads.
- **`app/audio_client.py`:** A threaded client that handles the persistent connection to the TTS server and smooth audio playback.
- **`server/tts_server.py`:** FastAPI entry point.
- **`server/model_loader.py`:** Handles the complexity of loading VibeVoice, managing CUDA devices, and caching voice presets.