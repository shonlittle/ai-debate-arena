import base64
from typing import Any

import httpx

from app.core.config import get_settings

ELEVENLABS_URL_TEMPLATE = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
ELEVENLABS_VOICES_URL = "https://api.elevenlabs.io/v1/voices"


async def list_voices() -> list[dict[str, str]]:
    settings = get_settings()
    if not settings.elevenlabs_api_key:
        raise RuntimeError("Missing ELEVENLABS_API_KEY")

    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.get(ELEVENLABS_VOICES_URL, headers=headers)
        response.raise_for_status()

    data: dict[str, Any] = response.json()
    voices: list[dict[str, str]] = []
    for raw_voice in data.get("voices", []):
        voice_id = str(raw_voice.get("voice_id", "")).strip()
        name = str(raw_voice.get("name", "")).strip()
        if voice_id and name:
            voices.append({"voice_id": voice_id, "name": name})

    if not voices:
        raise RuntimeError("No voices returned by ElevenLabs")

    return voices


async def synthesize_speech_mp3_base64(text: str, voice_id: str | None = None) -> str:
    settings = get_settings()
    if not settings.elevenlabs_api_key:
        raise RuntimeError("Missing ELEVENLABS_API_KEY")

    selected_voice_id = (voice_id or settings.elevenlabs_voice_id).strip()
    if not selected_voice_id:
        raise RuntimeError("Missing ElevenLabs voice id")

    url = ELEVENLABS_URL_TEMPLATE.format(voice_id=selected_voice_id)
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
