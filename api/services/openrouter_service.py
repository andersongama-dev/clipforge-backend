import os
import json
from typing import List, Dict, Any

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.shared_params import ResponseFormatJSONObject


OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "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"
)


def analyze_viral_clips(transcription_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
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
        '      "end": 48.3,\n        '
        '      "score": 9.7\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Do not include markdown, code fences, explanations, comments, or extra text."
    )

    user_content = json.dumps(
        transcription_data,
        ensure_ascii=False
    )

    system_message = ChatCompletionSystemMessageParam(
        role="system",
        content=system_prompt,
    )

    user_message = ChatCompletionUserMessageParam(
        role="user",
        content=user_content,
    )

    messages: List[ChatCompletionMessageParam] = [
        system_message,
        user_message,
    ]

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct",
            messages=messages,
            response_format=ResponseFormatJSONObject(
                type="json_object"
            ),
        )

        response_text = response.choices[0].message.content

        if not response_text:
            raise RuntimeError(
                "Received an empty response from OpenRouter."
            )

        parsed = json.loads(response_text)

        if not isinstance(parsed, dict):
            raise ValueError(
                "The response must be a JSON object."
            )

        clips = parsed.get("clips")

        if not isinstance(clips, list):
            raise ValueError(
                "'clips' must be a list."
            )

        return clips

    except Exception as e:
        raise RuntimeError(
            f"OpenRouter analysis failed: {e}"
        )