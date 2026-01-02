# ScreenBanter
Make your screen talk back. A DIY project built with VIBES to bridge Google’s Gemini Vision with Microsoft’s VibeVoice-0.5B for real-time desktop narration.

### 1. High-Level Architecture

The project is split into a **Frontend Daemon** (running in your system tray) and a **Local Inference Server** (running the TTS model).

---

### 2. Project Structure

```text
VisionVoice-Local/
├── app/
│   ├── main.py            # Orchestrator & System Tray
│   ├── capture.py         # DXcam high-speed screen grabbing
│   ├── vision.py          # Gemini 2.0 Flash Lite API client
│   └── audio_client.py    # Plays streaming audio chunks
├── server/
│   ├── tts_server.py      # FastAPI wrapper for VibeVoice
│   └── model_loader.py    # VibeVoice weights & CUDA setup
├── assets/                # Icons and loading sounds
└── .env                   # API Keys and local paths

```

---

### 3. Component Breakdown

#### A. The TTS Backend (FastAPI + VibeVoice)

Instead of returning a full file, we use **Streaming Response**. This allows the audio to start playing the moment the first few tokens are synthesized.

```python
# server/tts_server.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import torch
from vibevoice.model import VibeVoiceRealtime 

app = FastAPI()
model = VibeVoiceRealtime.from_pretrained("microsoft/VibeVoice-Realtime-0.5B").to("cuda")

@app.post("/v1/audio/stream")
async def stream_tts(text: str):
    def generate():
        # VibeVoice yields audio chunks incrementally
        for chunk in model.generate_stream(text):
            yield chunk.tobytes()
            
    return StreamingResponse(generate(), media_type="audio/wav")

```

#### B. The Vision Engine (DXcam + Gemini)

We use `DXcam` because it is **10x faster** than standard screenshot tools on Windows 11, capturing frames in roughly 5–10ms.

```python
# app/vision.py
import dxcam
from google import genai

camera = dxcam.create()

def get_screen_text(api_key):
    frame = camera.grab() # High-speed grab
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-lite',
        contents=['Extract text precisely. Text only.', frame]
    )
    return response.text.strip()

```

#### C. The System Tray Orchestrator

This keeps the app running in the background without a messy terminal window.

```python
# app/main.py
import pystray
from PIL import Image
from global_hotkeys import register_hotkeys, start_checking_hotkeys

def on_trigger():
    # 1. Capture & Gemini OCR
    text = get_screen_text(os.getenv("GEMINI_KEY"))
    
    # 2. Local Streaming TTS
    play_streaming_audio(text) # Uses PyAudio to play chunks from server

# System Tray Setup
image = Image.open("assets/icon.png")
menu = pystray.Menu(pystray.MenuItem('Exit', lambda icon: icon.stop()))
icon = pystray.Icon("VisionVoice", image, "VisionVoice Active", menu)

# Register Hotkey (Ctrl + Alt + S)
bindings = [["control + alt + s", None, on_trigger]]
register_hotkeys(bindings)

start_checking_hotkeys()
icon.run()

```

---

### 4. Implementation Roadmap for the Developer

| Phase | Focus | Key Tech |
| --- | --- | --- |
| **Phase 1** | **Backend Latency:** Set up the VibeVoice FastAPI server. Ensure it runs on CUDA (GPU) to hit the ~300ms first-byte target. | `torch`, `uvicorn` |
| **Phase 2** | **Capture Speed:** Implement `DXcam`. Test the speed difference against `Pillow`. | `dxcam`, `numpy` |
| **Phase 3** | **Cloud Bridge:** Integrate Gemini 2.0 Flash Lite. Optimize the prompt for minimal token usage to reduce API latency. | `google-genai` |
| **Phase 4** | **Async Audio:** Write the audio client. It must handle a "stream" of bytes and play them using `PyAudio` so there's no silence between chunks. | `pyaudio`, `requests` |
| **Phase 5** | **Packaging:** Bundle the app using `Nuitka` (better than PyInstaller for performance) so you have a single `.exe` that starts on boot. | `Nuitka` |

---

### 5. Estimated Performance (The 2026 Standard)

By using this specific stack, your end-to-end latency budget looks like this:

* **Capture (DXcam):** 10ms
* **Upload & Gemini OCR:** 600ms – 800ms
* **TTS Initialization (VibeVoice):** 300ms
* **Total:** **~1.1 Seconds** from Hotkey to Speech.

### Next Step

Would you like me to focus on the **Audio Client code**? This is often the hardest part—it requires playing the audio chunks in a "buffer" so the voice sounds smooth while the model is still generating the end of the sentence.

[VibeVoice-Realtime Setup and Performance](https://www.youtube.com/watch?v=TyupwtBoK_k)
This video provides a deep dive into the Microsoft VibeVoice-Realtime-0.5B model, detailing the installation and architectural nuances required to achieve the low-latency results discussed in this plan.
