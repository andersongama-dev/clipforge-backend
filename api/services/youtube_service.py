import os
from yt_dlp import YoutubeDL

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
UPLOADS_DIR = os.path.join(ROOT_DIR, 'uploads')

os.makedirs(UPLOADS_DIR, exist_ok=True)


def download_youtube_video(video_url: str) -> str:
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(UPLOADS_DIR, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            if not info:
                raise RuntimeError("Failed to extract video information.")

            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            final_mp4_path = f"{base}.mp4"

            if not os.path.exists(final_mp4_path):
                raise FileNotFoundError(f"Downloaded video file not found at expected path: {final_mp4_path}")

            return final_mp4_path

    except Exception as e:
        raise RuntimeError(f"YouTube download failed: {str(e)}")
