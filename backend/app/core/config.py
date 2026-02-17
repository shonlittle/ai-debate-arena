import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    xai_api_key: str
    elevenlabs_api_key: str
    elevenlabs_voice_id: str


def get_settings() -> Settings:
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "grok-4-fast-non-reasoning"),
        xai_api_key=os.getenv("XAI_API_KEY", ""),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    )
