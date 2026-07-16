import ffmpeg
import os
from typing import List, Dict, Any


def create_video_clip(video_path: str, output_path: str, start_time: float, end_time: float) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    duration = end_time - start_time

    try:
        (
            ffmpeg
            .input(video_path, ss=start_time)
            .output(
                output_path,
                t=duration,
                vcodec="libx264",
                acodec="aac",
                preset="fast"
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path

    except ffmpeg.Error as e:
        error = e.stderr.decode("utf-8") if e.stderr else str(e)
        raise RuntimeError(f"Video cutting error: {error}")


def cut_project_clips(video_path: str, clips: List[Dict[str, Any]], project_folder: str) -> List[str]:
    generated_clips = []

    PADDING_START = 3.0
    PADDING_END = 3.0

    for index, clip in enumerate(clips, start=1):
        raw_start = float(clip.get("start", 0.0))
        raw_end = float(clip.get("end", 0.0))

        start_time = max(0.0, raw_start - PADDING_START)
        end_time = raw_end + PADDING_END

        clip_filename = f"clip_{index:02d}.mp4"
        output_path = os.path.join(project_folder, clip_filename)

        create_video_clip(video_path, output_path, start_time, end_time)
        generated_clips.append(output_path)

    return generated_clips
