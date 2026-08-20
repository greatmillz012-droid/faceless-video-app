import requests
from openai import OpenAI

from ..config import settings


def generate_voiceover(text: str, output_path: str) -> str:
    if not settings.ELEVENLABS_API_KEY or not settings.ELEVENLABS_VOICE_ID:
        return generate_voiceover_openai_fallback(text, output_path)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.6},
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return output_path
    except requests.HTTPError as exc:
        response = exc.response
        if response is not None and response.status_code in (401, 402, 403):
            return generate_voiceover_openai_fallback(text, output_path)
        raise


def generate_voiceover_openai_fallback(text: str, output_path: str) -> str:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.audio.speech.create(model="tts-1", voice="onyx", input=text)
    resp.stream_to_file(output_path)
    return output_path
