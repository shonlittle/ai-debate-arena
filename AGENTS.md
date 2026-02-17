# AGENTS.md

This document provides guidance for AI coding agents and contributors working in this repository.

## Scope
- Applies to the entire repository unless a nested `AGENTS.md` overrides parts of this guidance.

## Project Setup
- Use Python virtual environment at `.venv`.
- Create if missing: `python3 -m venv .venv`
- Activate: `source .venv/bin/activate`
- Install dependencies (when present): `pip install -r requirements.txt`

## Python Standards
- Target Python 3.11+ unless otherwise specified.
- Follow PEP 8 and prefer clear, maintainable code over clever shortcuts.
- Add type hints to new/changed Python code where practical.
- Keep functions focused and small; avoid hidden side effects.

## Testing and Validation
- Run relevant tests after changes.
- If no tests exist, add focused tests for new behavior when feasible.
- If test tooling is present, prefer:
  - `pytest -q`
- For lint/format tooling, use project-configured commands if available.

## File and Change Hygiene
- Make minimal, scoped changes that solve the requested task.
- Do not refactor unrelated areas in the same change.
- Do not commit secrets, credentials, or local environment artifacts.
- Keep `.venv/` ignored by git.

## Agent Workflow Expectations
- Read this file before making edits.
- Explain assumptions when requirements are ambiguous.
- If blocked by missing context, ask focused questions.
- Summarize what changed and how it was validated.

## Commit and PR Guidance
- Use clear commit messages with intent and scope.
- Include a short validation note (tests/lint run) in PR descriptions.
- Highlight tradeoffs and follow-up work when relevant.
