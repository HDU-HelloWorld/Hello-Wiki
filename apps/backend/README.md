# Hello Wiki Backend (MVP Scaffold)

This directory contains an MVP backend skeleton that is minimally connected and runnable.
It intentionally excludes business logic implementations.

## Run

1. Create and activate a Python 3.11+ environment.
2. Install dependencies:
   - `pip install -e .`
3. Start development server:
   - `python main.py`

## API Endpoints

- `GET /api/`
- `GET /api/health`
- `GET /api/wiki` (501 placeholder)
- `POST /api/compile` (501 placeholder)
- `POST /api/qa` (501 placeholder)

## Directory Layout

- `src/api`: router assembly, endpoint placeholders, API dependencies
- `src/core`: settings, context, and database wiring placeholders
- `src/models`: SQLModel table definitions (minimal fields only)
- `src/schemas`: request/response schema placeholders
- `src/repositories`: repository interface placeholders
- `src/services`: service interface placeholders
- `src/workers`: async task registration placeholders

## Scope

- Includes only bootstrapping and structural wiring for MVP.
- Contains no domain/business implementation logic.
