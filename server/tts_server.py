# server/tts_server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from .model_loader import load_vibevoice_model
import pydantic

app = FastAPI(title="ScreenBanter TTS Server")

# Global model manager instance
manager, device = load_vibevoice_model()

class TTSRequest(pydantic.BaseModel):
    text: str

@app.post("/v1/audio/stream")
async def stream_tts(request: TTSRequest):
    if not manager:
        raise HTTPException(status_code=503, detail="TTS model not loaded")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    return StreamingResponse(manager.stream_audio(request.text), media_type="audio/wav")

@app.get("/health")
async def health_check():
    return {
        "status": "ok" if manager else "model_not_loaded",
        "device": device
    }
