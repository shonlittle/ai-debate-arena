import base64
import io
import math
import struct
import wave
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["debate"])

PERSONA_PRESETS: dict[str, str] = {
    "Scientist": "Evidence-driven and cautious.",
    "Philosopher": "Abstract, principled, and reflective.",
    "Economist": "Focuses on incentives and tradeoffs.",
    "Historian": "Grounded in precedent and context.",
    "Optimist": "Future-looking and solutions-oriented.",
}


class DebateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)
    persona_a: str = Field(..., min_length=2, max_length=50)
    persona_b: str = Field(..., min_length=2, max_length=50)
    turns: int = Field(6, ge=2, le=20)


class DebateTurn(BaseModel):
    turn_index: int
    speaker: Literal["persona_a", "persona_b"]
    persona: str
    text: str
    audio_mime_type: str
    audio_base64: str


class DebateResponse(BaseModel):
    topic: str
    turns: list[DebateTurn]



def _llm_generate_script_placeholder(payload: DebateRequest) -> list[tuple[str, str, str]]:
    """Returns (speaker, persona_name, utterance)."""
    persona_a_style = PERSONA_PRESETS.get(payload.persona_a, "Clear and direct.")
    persona_b_style = PERSONA_PRESETS.get(payload.persona_b, "Critical and analytical.")

    script: list[tuple[str, str, str]] = []
    for idx in range(payload.turns):
        if idx % 2 == 0:
            speaker = "persona_a"
            persona = payload.persona_a
            style = persona_a_style
        else:
            speaker = "persona_b"
            persona = payload.persona_b
            style = persona_b_style

        text = (
            f"Turn {idx + 1}: As {persona}, I argue about '{payload.topic}'. "
            f"Style note: {style} "
            f"Key point: {'support' if idx % 2 == 0 else 'challenge'} the core claim with one concrete reason."
        )
        script.append((speaker, persona, text))

    return script



def _generate_tone_wav_base64(frequency_hz: int = 440, duration_s: float = 0.7) -> str:
    sample_rate = 16000
    amplitude = 8000
    n_samples = int(sample_rate * duration_s)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            sample = int(amplitude * math.sin(2 * math.pi * frequency_hz * (i / sample_rate)))
            wav_file.writeframesraw(struct.pack("<h", sample))

    return base64.b64encode(buffer.getvalue()).decode("ascii")



def _tts_placeholder(text: str, turn_index: int) -> tuple[str, str]:
    """Placeholder for ElevenLabs call. Returns mime type and base64 audio."""
    del text
    frequency = 420 + ((turn_index % 4) * 50)
    audio_b64 = _generate_tone_wav_base64(frequency_hz=frequency)
    return "audio/wav", audio_b64


@router.post("/debate/generate", response_model=DebateResponse)
def generate_debate(payload: DebateRequest) -> DebateResponse:
    script_turns = _llm_generate_script_placeholder(payload)

    turns: list[DebateTurn] = []
    for idx, (speaker, persona, text) in enumerate(script_turns):
        mime_type, audio_b64 = _tts_placeholder(text=text, turn_index=idx)
        turns.append(
            DebateTurn(
                turn_index=idx,
                speaker=speaker,
                persona=persona,
                text=text,
                audio_mime_type=mime_type,
                audio_base64=audio_b64,
            )
        )

    return DebateResponse(topic=payload.topic, turns=turns)
