import os

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)