from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.elevenlabs_client import synthesize_speech_mp3_base64
from app.services.xai_client import generate_debate_turns

router = APIRouter(tags=["debate"])


class DebateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=300)
    persona_a: str = Field(..., min_length=2, max_length=80)
    persona_b: str = Field(..., min_length=2, max_length=80)
    turns: int = Field(6, ge=2, le=20)


class DebateTurnResponse(BaseModel):
    speaker: Literal["persona_a", "persona_b"]
    text: str
    audio_format: Literal["mp3"]
    audio_base64: str


class DebateResponse(BaseModel):
    topic: str
    turns: list[DebateTurnResponse]


@router.post("/debate", response_model=DebateResponse)
async def debate(payload: DebateRequest) -> DebateResponse:
    try:
        debate_turns = await generate_debate_turns(
            topic=payload.topic,
            persona_a=payload.persona_a,
            persona_b=payload.persona_b,
            turns=payload.turns,
        )
    except (httpx.HTTPError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=f"Debate generation failed: {exc}") from exc

    turns: list[DebateTurnResponse] = []
    for turn in debate_turns:
        try:
            audio_base64 = await synthesize_speech_mp3_base64(turn["text"])
        except (httpx.HTTPError, RuntimeError) as exc:
            raise HTTPException(status_code=502, detail=f"TTS failed: {exc}") from exc

        turns.append(
            DebateTurnResponse(
                speaker=turn["speaker"],
                text=turn["text"],
                audio_format="mp3",
                audio_base64=audio_base64,
            )
        )

    return DebateResponse(topic=payload.topic, turns=turns)
