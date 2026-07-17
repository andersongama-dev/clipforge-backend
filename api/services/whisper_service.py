import os
from typing import Dict, Any, List
import whisper
from pydub import AudioSegment

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


def transcribe_in_chunks(wav_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Audio file '{os.path.basename(wav_path)}' not found.")

    audio = AudioSegment.from_wav(wav_path)
    chunk_length_ms = 10 * 60 * 1000
    chunks_results = []
    temp_chunk_path = f"temp_{os.path.basename(wav_path)}"

    try:
        for start_ms in range(0, len(audio), chunk_length_ms):
            chunk = audio[start_ms: start_ms + chunk_length_ms]
            chunk.export(temp_chunk_path, format="wav")

            time_offset = start_ms / 1000.0
            result = transcribe_audio_wav(temp_chunk_path)

            adjusted_segments = []
            for segment in result["segments"]:
                adjusted_segments.append({
                    "start": segment["start"] + time_offset,
                    "end": segment["end"] + time_offset,
                    "text": segment["text"]
                })

            chunks_results.append({
                "text": result["text"],
                "segments": adjusted_segments
            })

        if os.path.exists(temp_chunk_path):
            os.remove(temp_chunk_path)

        return chunks_results

    except Exception as e:
        if os.path.exists(temp_chunk_path):
            os.remove(temp_chunk_path)
        raise RuntimeError(f"Chunk processing error: {str(e)}")