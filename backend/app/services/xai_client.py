import json
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings

XAI_CHAT_COMPLETIONS_URL = "https://api.x.ai/v1/chat/completions"


class _TurnModel(BaseModel):
    speaker: str
    text: str


class _DebateModel(BaseModel):
    turns: list[_TurnModel]


def _build_prompt(topic: str, persona_a: str, persona_b: str, turns: int, retry: bool) -> str:
    retry_instruction = ""
    if retry:
        retry_instruction = (
            "Your previous response was invalid. Return only valid JSON with the required shape."
        )

    return (
        "Create a debate script as strict JSON. "
        f"Topic: {topic}. Persona A: {persona_a}. Persona B: {persona_b}. "
        f"Total turns: {turns}. Speakers must alternate strictly starting with persona_a. "
        "Return JSON object with key 'turns', containing a list of objects "
        "with keys 'speaker' and 'text'. "
        "Speaker values must be exactly 'persona_a' or 'persona_b'. No markdown, no extra keys. "
        f"{retry_instruction}"
    )


def _parse_and_validate(raw_content: str, turns: int) -> list[dict[str, str]]:
    parsed = json.loads(raw_content)
    validated = _DebateModel.model_validate(parsed)

    if len(validated.turns) != turns:
        raise ValueError(f"Expected {turns} turns, got {len(validated.turns)}")

    output: list[dict[str, str]] = []
    for i, turn in enumerate(validated.turns):
        expected_speaker = "persona_a" if i % 2 == 0 else "persona_b"
        if turn.speaker != expected_speaker:
            raise ValueError(f"Turn {i} speaker must be {expected_speaker}, got {turn.speaker}")

        text = turn.text.strip()
        if not text:
            raise ValueError(f"Turn {i} text cannot be empty")

        output.append({"speaker": turn.speaker, "text": text})

    return output


async def generate_debate_turns(
    topic: str,
    persona_a: str,
    persona_b: str,
    turns: int,
) -> list[dict[str, str]]:
    settings = get_settings()
    if not settings.xai_api_key:
        raise RuntimeError("Missing XAI_API_KEY")

    headers = {
        "Authorization": f"Bearer {settings.xai_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        for attempt in range(2):
            payload: dict[str, Any] = {
                "model": settings.llm_provider,
                "temperature": 0.7,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a debate script generator. " "Always return strict JSON only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": _build_prompt(
                            topic=topic,
                            persona_a=persona_a,
                            persona_b=persona_b,
                            turns=turns,
                            retry=attempt == 1,
                        ),
                    },
                ],
            }

            response = await client.post(
                XAI_CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            try:
                return _parse_and_validate(content, turns=turns)
            except (
                json.JSONDecodeError,
                ValidationError,
                KeyError,
                IndexError,
                TypeError,
                ValueError,
            ):
                if attempt == 1:
                    raise RuntimeError("xAI returned invalid debate JSON")

    raise RuntimeError("xAI debate generation failed")
