import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse

from api.services.ffmpeg_service import handle_audio_extraction
from api.services.whisper_service import transcribe_audio_wav
from api.services.openrouter_service import analyze_viral_clips

app = FastAPI(title="ClipForge API")

UPLOAD_DIR = "uploads"
PROJECTS_DIR = "projects"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a video.")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Video saved successfully!"
    }


@app.post("/audio/extract-wav")
async def extract_audio_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )

    allowed_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"]
    _, ext = os.path.splitext(file.filename)

    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        generated_wav_path = handle_audio_extraction(file)

        return FileResponse(
            path=generated_wav_path,
            media_type="audio/wav",
            filename=os.path.basename(generated_wav_path)
        )

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


@app.post("/audio/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )

    allowed_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"]
    _, ext = os.path.splitext(file.filename)

    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        generated_wav_path = handle_audio_extraction(file)
        result = transcribe_audio_wav(generated_wav_path)
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


@app.post("/audio/analyze-clips")
async def analyze_clips_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )

    allowed_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"]
    _, ext = os.path.splitext(file.filename)

    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        generated_wav_path = handle_audio_extraction(file)
        transcription_data = transcribe_audio_wav(generated_wav_path)
        clips = analyze_viral_clips(transcription_data)

        filename_without_ext, _ = os.path.splitext(file.filename)
        project_folder = os.path.join(PROJECTS_DIR, filename_without_ext)
        os.makedirs(project_folder, exist_ok=True)

        clips_json_path = os.path.join(project_folder, "clips.json")
        with open(clips_json_path, "w", encoding="utf-8") as f:
            json.dump(clips, f, ensure_ascii=False, indent=2)

        return clips

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
