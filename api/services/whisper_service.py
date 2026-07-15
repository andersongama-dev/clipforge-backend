import whisper
import os
from typing import Dict, Any


def transcribe_audio_wav(wav_path: str) -> Dict[str, Any]:
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Audio file '{os.path.basename(wav_path)}' not found.")

    try:
        model = whisper.load_model("small")

        result = model.transcribe(
            wav_path,
            fp16=False,
            language="pt",
            no_speech_threshold=0.3,
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            condition_on_previous_text=False
        )

        segments_data = []
        for segment in result.get("segments", []):
            segments_data.append({
                "start": float(segment.get("start", 0.0)),
                "end": float(segment.get("end", 0.0)),
                "text": str(segment.get("text", "")).strip()
            })

        return {
            "text": str(result.get("text", "")).strip(),
            "segments": segments_data
        }

    except Exception as e:
        raise RuntimeError(f"Whisper transcription error: {str(e)}")
