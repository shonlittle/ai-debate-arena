# ai-debate-arena

AI Debate Arena MVP backend built with FastAPI, using xAI or OpenRouter for debate text and ElevenLabs for TTS.

## Backend Structure

```text
backend/
  app/
    api/debate.py
    core/config.py
    services/xai_client.py
    services/elevenlabs_client.py
    main.py
  tests/test_debate_api.py
  requirements.txt
  .env.example
```

## Environment

Create runtime env file from template:

```bash
cd backend
cp .env.example .env
```

Required vars in `backend/.env`:
- `LLM_PROVIDER` (`xai` or `openrouter`; backward-compatible with direct xAI model name)
- `LLM_MODEL` (model id used by the selected provider)
- `XAI_API_KEY`
- `OPENROUTER_API_KEY`
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID` (default voice preset provided)

`backend/.env.example` is template-only and contains no secrets.
Use `XAI_API_KEY` when `LLM_PROVIDER=xai`; use `OPENROUTER_API_KEY` when `LLM_PROVIDER=openrouter`.

## Run Backend Locally

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Debate endpoint:

```bash
curl -X POST http://localhost:8000/api/debate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Should cities ban private cars downtown?",
    "persona_a": "Voice A Name",
    "persona_b": "Voice B Name",
    "turns": 6,
    "persona_a_voice_id": "voice-id-a",
    "persona_b_voice_id": "voice-id-b"
  }'
```

Voices endpoint:

```bash
curl http://localhost:8000/api/voices
```

Response shape:

```json
{
  "topic": "...",
  "turns": [
    {
      "speaker": "persona_a",
      "text": "...",
      "audio_format": "mp3",
      "audio_base64": "..."
    }
  ]
}
```

## Test

```bash
cd backend
source ../.venv/bin/activate
pytest -q
```

The test mocks xAI and ElevenLabs calls and validates `/api/debate` response structure and base64 audio fields.
