import ffmpeg
import os
from fastapi import UploadFile

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))

UPLOADS_DIR = os.path.join(ROOT_DIR, 'uploads')
AUDIOS_DIR = os.path.join(ROOT_DIR, 'audios')

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(AUDIOS_DIR, exist_ok=True)

def handle_audio_extraction(file: UploadFile) -> str:
    filename = file.filename
    if not filename:
        raise ValueError("Filename is missing.")

    video_path = os.path.join(UPLOADS_DIR, filename)

    filename_without_ext, _ = os.path.splitext(filename)
    audio_filename = f"{filename_without_ext}.wav"
    wav_path = os.path.join(AUDIOS_DIR, audio_filename)

    try:
        with open(video_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                buffer.write(chunk)

        (
            ffmpeg
            .input(video_path)
            .output(wav_path, acodec='pcm_s16le', ac=2, ar='44100')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"Success! Audio saved in: {wav_path}")
        return wav_path

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
        raise RuntimeError(f"FFmpeg processing error: {error_msg}")

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)