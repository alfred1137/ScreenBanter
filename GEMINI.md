# ScreenBanter

## Project Overview
ScreenBanter is a real-time desktop narration application. It captures screen content, uses Google's Gemini API for text extraction (OCR), and then reads the text aloud using a locally hosted VibeVoice TTS model.

### Key Components
1.  **Frontend Daemon**: System tray app, screen capture, Gemini API integration.
2.  **TTS Server**: Local FastAPI server for VibeVoice inference.

## Technology Stack
- **Core**: Python 3.10+
- **Manager**: uv
- **AI/ML**: Google Gemini (Vision), VibeVoice (TTS)
- **Web**: FastAPI, Uvicorn
- **Desktop**: DXcam (Capture), pystray (Tray), global_hotkeys

## Architecture Principles
- **Modular Design**: Single responsibility per file.
- **Async First**: Critical for I/O and Model inference.
- **Type Safety**: Full typing coverage required.

## Memory Bank
The project context is maintained in the `memory-bank/` directory.
- [Project Brief](memory-bank/projectBrief.md)
- [Product Context](memory-bank/productContext.md)
- [System Patterns](memory-bank/systemPatterns.md)
- [Tech Context](memory-bank/techContext.md)
- [Active Context](memory-bank/activeContext.md)
- [Progress](memory-bank/progress.md)

## Development Skills & Rules
This project follows strict development guidelines encapsulated in Agent Skills.
- **FastAPI Development**: See `.gemini/skills/fastapi-development/SKILL.md`
- **ML Workflow**: See `.gemini/skills/python-ml-workflow/SKILL.md`

## Quick Start
```bash
# Install uv
pip install uv

# Setup
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt

# Run Server
uvicorn server.tts_server:app --reload

# Run Client
python app/main.py
```
