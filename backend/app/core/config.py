import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    llm_model: str
    xai_api_key: str
    openrouter_api_key: str
    elevenlabs_api_key: str
    elevenlabs_voice_id: str


def get_settings() -> Settings:
    llm_provider_raw = os.getenv("LLM_PROVIDER", "xai").strip()
    llm_model = os.getenv("LLM_MODEL", "").strip()

    if llm_provider_raw in {"xai", "openrouter"}:
        llm_provider = llm_provider_raw
    else:
        # Backward-compatible mode: allow model name in LLM_PROVIDER and default provider to xAI.
        llm_provider = "xai"
        if not llm_model:
            llm_model = llm_provider_raw

    if not llm_model:
        llm_model = (
            "x-ai/grok-4-fast:free" if llm_provider == "openrouter" else "grok-4-fast-non-reasoning"
        )

    return Settings(
        llm_provider=llm_provider,
        llm_model=llm_model,
        xai_api_key=os.getenv("XAI_API_KEY", ""),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
    )
