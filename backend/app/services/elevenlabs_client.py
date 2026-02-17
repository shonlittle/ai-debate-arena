import base64

import httpx

from app.core.config import get_settings

ELEVENLABS_URL_TEMPLATE = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


async def synthesize_speech_mp3_base64(text: str) -> str:
    settings = get_settings()
    if not settings.elevenlabs_api_key:
        raise RuntimeError("Missing ELEVENLABS_API_KEY")

    url = ELEVENLABS_URL_TEMPLATE.format(voice_id=settings.elevenlabs_voice_id)
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "output_format": "mp3_44100_128",
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    return base64.b64encode(response.content).decode("ascii")
