import os
import json
from typing import List, Dict, Any, cast
from openai import OpenAI
from openai.types.chat import ChatCompletion

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "your_openrouter_api_key_here")


def analyze_viral_clips(transcription_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": "https://github.com",
            "X-Title": "ClipForge API"
        }
    )

    system_prompt = (
        "You are an expert in creating viral content for TikTok, YouTube Shorts, and Instagram Reels.\n"
        "Analyze the provided JSON transcription containing timestamps and text segments.\n\n"
        "Select between 3 and 7 clip ranges with the highest retention potential based on:\n"
        "- Strong hook\n"
        "- Valuable information\n"
        "- Controversy\n"
        "- Curiosity\n"
        "- Interesting story\n"
        "- High emotional impact\n\n"
        "Return ONLY a valid JSON object in this format:\n\n"
        "{\n"
        '  "clips": [\n'
        "    {\n"
        '      "title": "Clip Title",\n'
        '      "start": 12.5,\n'
        '      "end": 48.3,\n'
        '      "score": 9.7\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Do not include markdown, code fences, explanations, comments, or extra text."
    )

    user_content = json.dumps(transcription_data, ensure_ascii=False)

    try:
        raw_response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )

        response = cast(ChatCompletion, raw_response)

        if not response.choices or not response.choices[0].message:
            raise RuntimeError("Received an empty response structure from OpenRouter.")

        response_text = response.choices[0].message.content
        if not response_text:
            raise RuntimeError("Received an empty response text from OpenRouter.")

        parsed = json.loads(response_text.strip())

        if isinstance(parsed, list):
            return parsed

        if isinstance(parsed, dict):
            clips = parsed.get("clips")
            if isinstance(clips, list):
                return clips

            for key, value in parsed.items():
                if isinstance(value, list):
                    return value

        raise ValueError("Model response could not be parsed into a valid list of clips.")

    except Exception as e:
        raise RuntimeError(f"OpenRouter analysis failed: {e}")

def analyze_multiple_chunks(chunks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    all_clips = []

    for chunk in chunks_data:
        if not chunk.get("text"):
            continue

        try:
            clips = analyze_viral_clips(chunk)
            all_clips.extend(clips)
        except Exception as e:
            print(f"Warning: Failed to analyze chunk: {e}")
            continue

    return all_clips