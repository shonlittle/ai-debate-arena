# ai-debate-arena

Minimal full-stack MVP for generating and playing an AI debate script.

## Stack
- Backend: FastAPI (Python)
- Frontend: React + Vite (TypeScript)

## Project Structure

```text
backend/
  app/main.py
  app/api/debate.py
  requirements.txt
  .env.example
  tests/test_debate_api.py

frontend/
  src/
  package.json
  .env.example

README.md
```

## Features (MVP)
1. User provides topic, two personas, and debate length.
2. Backend generates a debate script (placeholder LLM logic).
3. Backend adds per-turn placeholder TTS audio (base64 WAV, ElevenLabs-ready integration point).
4. Frontend plays turns sequentially and shows subtitles.

## Prerequisites
- Python 3.11+
- Node.js 18+

## Backend Setup

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Note: `.env.example` is a template only. Runtime configuration is read from `backend/.env`.

Health check: `GET http://localhost:8000/health`

Generate endpoint: `POST http://localhost:8000/api/debate/generate`

Example payload:

```json
{
  "topic": "Should schools adopt AI tutors?",
  "persona_a": "Scientist",
  "persona_b": "Philosopher",
  "turns": 6
}
```

## Frontend Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and calls backend URL from `VITE_API_BASE_URL`.
Note: `.env.example` is a template only. Vite reads values from `frontend/.env`.

## Docker Compose

Run both services with Docker:

```bash
docker compose up --build
```

Host URLs:
- Frontend: `http://localhost:5174`
- Backend API: `http://localhost:8001`

Why these ports:
- `8000` is already in use on this machine, so compose maps backend to `8001:8000`.
- `5174` is used for frontend to avoid interfering with any local Vite session.
- Compose reads `backend/.env` and `frontend/.env` (not `.env.example`).

## Lint / Format

Backend (from `backend/`):

```bash
source ../.venv/bin/activate
ruff check .
black --check .
```

Frontend (from `frontend/`):

```bash
npm run lint
npm run format
```

## Test

From `backend/`:

```bash
source ../.venv/bin/activate
pytest -q
```

The included test validates that `/api/debate/generate` returns the expected response structure.

## Notes on Integrations
- LLM generation is currently a placeholder in `backend/app/api/debate.py` (`_llm_generate_script_placeholder`).
- ElevenLabs TTS is currently a placeholder tone generator in `backend/app/api/debate.py` (`_tts_placeholder`).
- Replace these two functions with real provider calls when credentials and provider SDK/API details are available.
