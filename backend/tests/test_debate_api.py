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


async def _fake_synthesize_speech_mp3_base64(text: str) -> str:
    return base64.b64encode(f"audio:{text}".encode("utf-8")).decode("ascii")


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
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["topic"] == "Should cities ban cars from downtown?"
    assert isinstance(data["turns"], list)
    assert len(data["turns"]) == 6

    for i, turn in enumerate(data["turns"]):
        expected_speaker = "persona_a" if i % 2 == 0 else "persona_b"
        assert turn["speaker"] == expected_speaker
        assert isinstance(turn["text"], str) and turn["text"]
        assert turn["audio_format"] == "mp3"
        assert isinstance(turn["audio_base64"], str) and turn["audio_base64"]

        decoded = base64.b64decode(turn["audio_base64"])
        assert decoded.startswith(b"audio:")
