import os
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse

from api.services.ffmpeg_service import handle_audio_extraction

app = FastAPI(title="ClipForge API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)