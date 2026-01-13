# ScreenBanter

**Make your screen talk back.**

ScreenBanter is a DIY project that bridges **Google’s Gemini Vision** (for OCR) with **Microsoft’s VibeVoice-0.5B** (for local TTS) to provide real-time desktop narration. It features instant capture-to-speech and a multi-screenshot queuing system.

---

## 🚀 Features

- **Instant Narration:** Press `Ctrl+Alt+S` to capture the screen and hear the text immediately.
- **Batch Mode:** Use `F10` to queue multiple screenshots (e.g., different pages or windows) and `F11` to stitch them together and narrate them as one cohesive text.
- **Local Neural TTS:** Uses VibeVoice-0.5B with GPU acceleration for natural, low-latency speech.
- **Smart OCR:** Leverages Gemini 2.0 Flash Lite to intelligently merge fragmented text and paragraphs.
- **Non-Intrusive:** Runs in the system tray with audio feedback for interactions.

---

## 🛠️ Architecture

The project is split into two components:
1.  **Frontend Daemon:** A system tray application (`app/main.py`) that handles global hotkeys, screen capture (via `DXcam`), and audio playback (`PyAudio`).
2.  **Local Inference Server:** A FastAPI server (`server/tts_server.py`) that hosts the VibeVoice model and streams audio chunks to the client.

---

## 📦 Installation

**Prerequisites:**
- Windows 10/11 (Required for `DXcam`).
- NVIDIA GPU with CUDA support (Recommended for VibeVoice latency).
- [uv](https://github.com/astral-sh/uv) (Recommended for Python dependency management).
- [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Required for `pyaudio` and `pystray`).

**1. Clone the Repository:**
```bash
git clone https://github.com/yourusername/ScreenBanter.git
cd ScreenBanter
```

**2. Setup Environment:**
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Edit `.env` and add your **GEMINI_KEY**.

**3. Install Dependencies:**
Using `uv`:
```bash
uv sync
```
*Note: The project pins `transformers` to 4.51.3 and uses CUDA 12.1-compatible PyTorch.*

---

## 🎮 Usage

**1. Start the Application:**
This command starts the system tray app, which automatically launches the TTS server in the background.
```bash
uv run python -m app.main
```
*Wait for the startup announcement: "ScreenBanter is active..."*

**2. Controls:**

| Hotkey | Action | Description |
| :--- | :--- | :--- |
| **`Ctrl + Alt + S`** | **Instant Capture** | Captures the current screen and narrates identified text immediately. |
| **`F10`** | **Queue Screenshot** | Captures the screen and adds it to a buffer. You will hear a confirmation beep. |
| **`F11`** | **Process Queue** | Sends all queued screenshots to Gemini, merges the text, and narrating the result. |

**3. Logs:**
- OCR results are logged to `logs/ocr.log`.

---

## 🔧 Technical Details

### Project Structure
```text
ScreenBanter/
├── app/
│   ├── main.py            # Orchestrator, System Tray, & Hotkeys
│   ├── capture.py         # DXcam high-speed screen grabbing
│   ├── vision.py          # Gemini Vision API client (Multi-image support)
│   └── audio_client.py    # Threaded audio streaming client
├── server/
│   ├── tts_server.py      # FastAPI wrapper for VibeVoice
│   └── model_loader.py    # Model weights, caching, and CUDA setup
├── third_party/           # Submodules (VibeVoice)
└── assets/                # Icons and resources
```

### Performance Targets
- **Capture (DXcam):** ~10ms
- **OCR (Gemini):** ~600-800ms
- **TTS Initialization (VibeVoice):** ~300ms (Warm)
- **Total Latency:** ~1.1 - 1.5 seconds (Warm state)

*Note: The first request after startup may take longer (up to 10s) as the model loads into VRAM.*