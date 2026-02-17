# AGENTS.md – AI Debate Arena

## Project Overview

AI Debate Arena is a full-stack application that generates multi-persona debates using LLMs and synthesizes voice output using ElevenLabs.

## Tech Stack

- Backend: Python (FastAPI)
- Frontend: React + Vite + TypeScript
- Voice: ElevenLabs
- LLM: OpenAI GPT models (API)

## Coding Standards

- Python: Black formatting, type hints required
- TypeScript: Strict mode enabled
- Keep functions small and composable
- Avoid unnecessary abstraction

## Architecture Guidelines

- Debate generation logic lives in backend service layer
- API responses must be JSON-serializable
- Audio generation should be abstracted behind a service
- Environment variables must be documented in .env.example

## Testing

- Backend endpoints should have at least one pytest test
- Avoid external API calls in unit tests (mock them)

## Development Principles

- Keep MVP simple
- Prefer clarity over cleverness
- Optimize for iteration speed
