import base64

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


async def _fake_generate_debate_turns(
    topic: str,
    persona_a: str,
    persona_b: str,
    turns: int,
) -> list[dict[str, str]]:
    del topic
    output: list[dict[str, str]] = []
    for i in range(turns):
        if i % 2 == 0:
            output.append({"speaker": "persona_a", "text": f"{persona_a} turn {i + 1}"})
        else:
            output.append({"speaker": "persona_b", "text": f"{persona_b} turn {i + 1}"})
    return output


async def _fake_synthesize_speech_mp3_base64(text: str, voice_id: str | None = None) -> str:
    marker = voice_id or "default"
    return base64.b64encode(f"audio:{marker}:{text}".encode("utf-8")).decode("ascii")


async def _fake_list_voices() -> list[dict[str, str]]:
    return [
        {"voice_id": "voice-a", "name": "Alpha"},
        {"voice_id": "voice-b", "name": "Beta"},
    ]


def test_debate_endpoint_returns_required_shape(monkeypatch) -> None:
    monkeypatch.setattr("app.api.debate.generate_debate_turns", _fake_generate_debate_turns)
    monkeypatch.setattr(
        "app.api.debate.synthesize_speech_mp3_base64",
        _fake_synthesize_speech_mp3_base64,
    )

    response = client.post(
        "/api/debate",
        json={
            "topic": "Should cities ban cars from downtown?",
            "persona_a": "Scientist",
            "persona_b": "Economist",
            "turns": 6,
            "persona_a_voice_id": "voice-a",
            "persona_b_voice_id": "voice-b",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["topic"] == "Should cities ban cars from downtown?"
    assert isinstance(data["turns"], list)
    assert len(data["turns"]) == 6

    for i, turn in enumerate(data["turns"]):
        expected_speaker = "persona_a" if i % 2 == 0 else "persona_b"
        expected_voice = "voice-a" if i % 2 == 0 else "voice-b"

        assert turn["speaker"] == expected_speaker
        assert isinstance(turn["text"], str) and turn["text"]
        assert turn["audio_format"] == "mp3"
        assert isinstance(turn["audio_base64"], str) and turn["audio_base64"]

        decoded = base64.b64decode(turn["audio_base64"])
        assert decoded.startswith(f"audio:{expected_voice}:".encode("utf-8"))


def test_voices_endpoint_returns_voice_list(monkeypatch) -> None:
    monkeypatch.setattr("app.api.debate.list_voices", _fake_list_voices)

    response = client.get("/api/voices")
    assert response.status_code == 200

    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) == 2
    assert data["voices"][0]["voice_id"] == "voice-a"
    assert data["voices"][1]["name"] == "Beta"
