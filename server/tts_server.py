# server/tts_server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from .model_loader import load_vibevoice_model
import pydantic
import psutil
import os
import sys

app = FastAPI(title="ScreenBanter TTS Server")

# Global model manager instance
manager, device = load_vibevoice_model()

class TTSRequest(pydantic.BaseModel):
    text: str
    voice_key: str = None

@app.post("/v1/audio/stream")
async def stream_tts(request: TTSRequest):
    if not manager:
        raise HTTPException(status_code=503, detail="TTS model not loaded")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    return StreamingResponse(manager.stream_audio(request.text, voice_key=request.voice_key), media_type="audio/wav")

@app.get("/v1/voices")
async def get_voices():
    if not manager:
        raise HTTPException(status_code=503, detail="TTS model not loaded")
    return {"voices": manager.get_available_voices()}

@app.on_event("startup")
async def startup_sequence():
    """
    Initializes system priority and warms up the VibeVoice model.
    """
    # 1. Set Process Priority
    try:
        p = psutil.Process(os.getpid())
        if sys.platform == "win32":
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            print("✅ Process priority set to HIGH_PRIORITY_CLASS")
    except Exception as e:
        print(f"⚠️ Failed to set high priority: {e}")

    # 2. Warmup Model
    if manager:
        print("[Warmup] Starting model warmup...")
        try:
            # 1. Load default voice preset into VRAM
            if manager.default_voice_key:
                print(f"[Warmup] Caching default voice: {manager.default_voice_key}")
                manager._ensure_voice_cached(manager.default_voice_key)
            
            # 2. Run a dummy generation to trigger CUDA JIT / context init
            print("[Warmup] Running dummy generation...")
            dummy_text = "Ready."
            # Consume the generator to force execution
            for _ in manager.stream_audio(dummy_text):
                pass
            print("[Warmup] Model warmup complete. First request should be fast.")
        except Exception as e:
            print(f"[Warmup] Warning: Warmup failed: {e}")

@app.get("/health")
async def health_check():
    return {
        "status": "ok" if manager else "model_not_loaded",
        "device": device
    }
