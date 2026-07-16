import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api.services.ffmpeg_service import handle_audio_extraction
from api.services.whisper_service import transcribe_audio_wav
from api.services.openrouter_service import analyze_viral_clips
from api.services.video_service import cut_project_clips
from api.services.youtube_service import download_youtube_video

app = FastAPI(title="ClipForge API")

UPLOAD_DIR = "uploads"
PROJECTS_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)


class YouTubeRequest(BaseModel):
    url: str

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is missing.")

    allowed_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"]
    _, ext = os.path.splitext(file.filename)

    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        )

    filename_without_ext, _ = os.path.splitext(file.filename)
    project_folder = os.path.join(PROJECTS_DIR, filename_without_ext)
    os.makedirs(project_folder, exist_ok=True)

    project_video_path = os.path.join(project_folder, file.filename)

    try:
        with open(project_video_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        generated_wav_path = handle_audio_extraction(project_video_path)

        return FileResponse(
            path=generated_wav_path,
            media_type="audio/wav",
            filename=os.path.basename(generated_wav_path)
        )

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")

    finally:
        if os.path.exists(project_video_path):
            os.remove(project_video_path)


@app.post("/audio/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is missing.")

    allowed_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"]
    _, ext = os.path.splitext(file.filename)

    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        )

    filename_without_ext, _ = os.path.splitext(file.filename)
    project_folder = os.path.join(PROJECTS_DIR, filename_without_ext)
    os.makedirs(project_folder, exist_ok=True)

    project_video_path = os.path.join(project_folder, file.filename)

    try:
        with open(project_video_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        generated_wav_path = handle_audio_extraction(project_video_path)
        result = transcribe_audio_wav(generated_wav_path)
        return result

    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")

    finally:
        if os.path.exists(project_video_path):
            os.remove(project_video_path)


@app.post("/audio/analyze-clips")
async def analyze_clips_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is missing.")

    allowed_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"]
    _, ext = os.path.splitext(file.filename)

    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        )

    filename_without_ext, _ = os.path.splitext(file.filename)
    project_folder = os.path.join(PROJECTS_DIR, filename_without_ext)
    os.makedirs(project_folder, exist_ok=True)

    project_video_path = os.path.join(project_folder, file.filename)

    try:
        with open(project_video_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        generated_wav_path = handle_audio_extraction(project_video_path)
        transcription_data = transcribe_audio_wav(generated_wav_path)
        clips = analyze_viral_clips(transcription_data)

        clips_json_path = os.path.join(project_folder, "clips.json")
        with open(clips_json_path, "w", encoding="utf-8") as f:
            json.dump(clips, f, ensure_ascii=False, indent=2)

        cut_project_clips(project_video_path, clips, project_folder)

        return {
            "project": filename_without_ext,
            "message": f"Successfully generated {len(clips)} video clips and clips.json.",
            "clips": clips
        }

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")

@app.post("/audio/analyze-clips-youtube")
async def analyze_clips_youtube_endpoint(request: YouTubeRequest):
    try:
        downloaded_video_path = download_youtube_video(request.url)
        video_filename = os.path.basename(downloaded_video_path)
        filename_without_ext, _ = os.path.splitext(video_filename)

        project_folder = os.path.join(PROJECTS_DIR, filename_without_ext)
        os.makedirs(project_folder, exist_ok=True)

        project_video_path = os.path.join(project_folder, video_filename)
        os.rename(downloaded_video_path, project_video_path)

        generated_wav_path = handle_audio_extraction(project_video_path)
        transcription_data = transcribe_audio_wav(generated_wav_path)
        clips = analyze_viral_clips(transcription_data)

        clips_json_path = os.path.join(project_folder, "clips.json")
        with open(clips_json_path, "w", encoding="utf-8") as f:
            json.dump(clips, f, ensure_ascii=False, indent=2)

        cut_project_clips(project_video_path, clips, project_folder)

        return {
            "project": filename_without_ext,
            "message": f"Successfully downloaded, analyzed and generated {len(clips)} clips.",
            "clips": clips
        }

    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")

    finally:
        if 'project_video_path' in locals() and os.path.exists(project_video_path):
            os.remove(project_video_path)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
