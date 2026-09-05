from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import tempfile
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load local .env files if present (safely ignored on Render)
load_dotenv()

# Explicitly configure the Gemini API key using Render's environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

from anadi_voice_engine import (
    convert_audio_to_text,
    convert_text_to_audio
)

from backend.routes.query import router as query_router


app = FastAPI()


# Allow requests from the React/Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "SAHAKAAR KIOSK backend is running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "SAHAKAAR KIOSK backend"
    }


@app.post("/voice/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    temp_path = None

    try:
        suffix = os.path.splitext(file.filename or ".webm")[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(await file.read())
            temp_path = temp_file.name

        text, language = convert_audio_to_text(temp_path)

        return {
            "text": text,
            "language": language
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice transcription failed: {str(e)}"
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/voice/speak")
async def speak_voice(data: dict):
    try:
        text = data.get("text", "")
        language = data.get("language", "en")

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty"
            )

        audio_base64 = convert_text_to_audio(
            text,
            language
        )

        if not audio_base64:
            raise HTTPException(
                status_code=500,
                detail="TTS failed"
            )

        return {
            "audio": audio_base64,
            "language": language
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice synthesis failed: {str(e)}"
        )


# KEEP THIS AT THE VERY END
app.include_router(query_router)