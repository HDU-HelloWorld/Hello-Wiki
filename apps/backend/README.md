# Hello Wiki Backend (Layered MVP Scaffold)

This directory contains a layered MVP backend skeleton that is minimally connected and runnable.
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

- `src/api`: external routes, request/response conversion, application wiring
- `src/application`: use-case orchestration layer
- `src/core`: config, request context, auth/audit/tracing placeholders
- `src/domain`: domain entities and abstract ports
- `src/infra`: external adapters/providers implementing domain ports
- `src/workers`: asynchronous orchestration boundaries and task registration placeholders

## Layer Dependency Rule

- Allowed: `api -> application -> domain`
- Allowed: `application -> infra` (through dependency/provider wiring)
- Allowed: `workers -> application`
- Allowed: `all -> core`
- Forbidden: `domain -> api|infra|workers`
- Forbidden: `api -> infra` direct calls

## Scope

- Includes only bootstrapping and structural wiring for MVP.
- Contains no domain/business implementation logic.
