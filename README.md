# ai-debate-arena

AI Debate Arena is a full-stack MVP that generates a debate script with an LLM and synthesizes per-turn audio with ElevenLabs.

## Demo
- Loom walkthrough: [AI Debate Arena Live Demo](https://www.loom.com/share/c76d4e1bc28a42a4af23a8e2b2e06326)

## Stack
- Backend: FastAPI (Python)
- Frontend: React + Vite (TypeScript)
- LLM Providers: xAI or OpenRouter
- TTS: ElevenLabs

## Project Structure

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

frontend/
  src/
  package.json
  .env.example

docker-compose.yml
README.md
```

## Features
- Fetch available ElevenLabs voices via backend.
- Select one voice for Persona A and a different voice for Persona B in frontend.
- Optional humor mode toggle for overblown, exaggerated comedic debates.
- Generate alternating debate turns from LLM.
- Synthesize each turn as MP3 and return base64 audio.
- Play generated turns sequentially in frontend with live subtitle text.

## Environment Variables

`backend/.env` (copy from `backend/.env.example`):
- `LLM_PROVIDER`: `xai` or `openrouter`
  - Backward-compatible: if you set an xAI model name directly, it is treated as xAI mode.
- `LLM_MODEL`: model id for selected provider.
- `XAI_API_KEY`: required when using xAI.
- `OPENROUTER_API_KEY`: required when using OpenRouter.
- `ELEVENLABS_API_KEY`: required for TTS and voices listing.
- `ELEVENLABS_VOICE_ID`: fallback voice id if per-persona voice ids are not sent.

`frontend/.env` (copy from `frontend/.env.example`):
- `VITE_API_BASE_URL`: backend base URL (default in example: `http://localhost:8001`).

Notes:
- `.env.example` files are templates only.
- `.env` files are git-ignored and should not be committed.

## Local Development (without Docker)

### 1) Backend

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend health check:

```bash
curl http://localhost:8000/health
```

### 2) Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

## Docker Compose

Run both services:

```bash
docker compose up --build
```

Exposed host ports:
- Frontend: `http://localhost:5174`
- Backend: `http://localhost:8001`

Compose uses:
- `backend/.env`
- `frontend/.env`

If you change env vars, recreate services:

```bash
docker compose up -d --build --force-recreate backend frontend
```

## API

### GET `/health`
Returns:

```json
{"status":"ok"}
```

### GET `/api/voices`
Returns a trimmed voice list from ElevenLabs:

```json
{
  "voices": [
    { "voice_id": "...", "name": "..." }
  ]
}
```

### POST `/api/debate`
Request:

```json
{
  "topic": "Should AI replace homework?",
  "persona_a": "Laura",
  "persona_b": "Adam",
  "turns": 6,
  "humor_mode": true,
  "persona_a_voice_id": "voice-id-a",
  "persona_b_voice_id": "voice-id-b"
}
```

Response:

```json
{
  "topic": "Should AI replace homework?",
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

Curl example (Docker port):

```bash
curl -X POST http://localhost:8001/api/debate \
  -H "Content-Type: application/json" \
  -d '{
    "topic":"Should AI replace homework?",
    "persona_a":"Persona A",
    "persona_b":"Persona B",
    "turns":6,
    "humor_mode":true,
    "persona_a_voice_id":"voice-id-a",
    "persona_b_voice_id":"voice-id-b"
  }'
```

## Lint / Format / Tests

Backend:

```bash
cd backend
source ../.venv/bin/activate
ruff check .
black --check .
pytest -q
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
npm run format
```

## Troubleshooting
- `502 Debate generation failed ... 403/404`: invalid or unavailable LLM key/model/provider combination.
- `502 TTS failed ... 401`: invalid ElevenLabs API key in running container/process.
- `quota_exceeded` from ElevenLabs: increase ElevenLabs usage limit/credits.
- CORS errors from frontend: ensure backend includes your frontend origin (`5174` for Docker frontend).
