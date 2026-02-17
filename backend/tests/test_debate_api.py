from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_generate_debate_returns_valid_structure() -> None:
    response = client.post(
        "/api/debate/generate",
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
        assert turn["turn_index"] == i
        assert turn["speaker"] in {"persona_a", "persona_b"}
        assert isinstance(turn["persona"], str) and turn["persona"]
        assert isinstance(turn["text"], str) and turn["text"]
        assert turn["audio_mime_type"] == "audio/wav"
        assert isinstance(turn["audio_base64"], str) and turn["audio_base64"]
