# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Hello-Wiki** is a pnpm workspace monorepo for a Wiki platform with AI-powered features. Currently in MVP/scaffold stage.

- `apps/web`: Next.js 16 + React 19 + TypeScript + Tailwind CSS v4
- `apps/backend`: FastAPI backend with Clean Architecture + CQRS + DDD

## Development Commands

### Root (Monorepo)
```bash
pnpm install              # Install all workspace dependencies
pnpm dev                  # Start both web and backend in dev mode (parallel)
pnpm build                # Build web application only
pnpm lint                 # Run ESLint on web
```

### Frontend (`apps/web`)
```bash
pnpm dev                  # Next.js dev server (port 3000)
pnpm build                # Production build
pnpm lint                 # ESLint check
```

### Backend (`apps/backend`)
```bash
# Setup
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Running
python run.py              # Start API server (localhost:8000)
python worker.py           # Start async worker

# Testing
python3 -m pytest tests/ -q              # Run all tests
python3 -m pytest tests/test_gateway.py -v  # Specific test file

# Linting & Type Checking
ruff check src/ tests/     # Lint
ruff check --fix src/ tests/  # Auto-fix
ruff format src/ tests/    # Format
mypy src/                  # Type check
lint-imports               # Architecture verification (import-linter)
```

## Architecture

### Backend: Clean Architecture + CQRS + DDD

Strict layered architecture enforced by **import-linter** (8 contracts in `pyproject.toml`):

```
Entry Layers (top)
├── src/api/          # HTTP routes, schemas, assemblers, gateway
├── src/workers/      # Background tasks (TaskIQ)
    ↓
Application Layer
├── src/application/  # Use case orchestration (chat, wiki, ingest, maintenance)
    ↓
Infrastructure Layer
├── src/infrastructure/  # Implementations (ai/, db/, parser/, storage/)
    ↓
Domain Layer
├── src/domain/       # Business rules, entities, ports
    ↓
Core Layer (bottom)
└── src/core/         # Config, logging, context, tracing
```

**Key Constraints:**
- Layered dependency direction only (no reverse imports)
- Application modules (chat/wiki/ingest/maintenance) are independent
- Core layer has no upper layer imports
- Domain layer has no web framework dependencies
- Application layer cannot depend on API schemas
- API routes cannot directly access domain layer

### Frontend: Next.js 16 App Router

```
apps/web/src/
├── app/              # Routes (page.tsx, layout.tsx)
├── component/        # React components
├── lib/              # Utilities
└── assets/           # Static assets
```

## Multi-Tenancy

- Tenant ID passed via `X-Workspace-ID` header
- Gateway validates UUID format
- ContextVars inject workspace_id globally for async layers
- Default tenant: `00000000-0000-0000-0000-000000000001`

## CI Pipeline

Runs on `push` and `pull_request`:
- Frontend: pnpm lint, pnpm build
- Backend: lint-imports, mypy, ruff check, ruff format --check, pytest

## Environment Requirements

- Node.js >=22.19.0
- pnpm 10
- Python 3.11+

## Important Notes

<!-- BEGIN:nextjs-agent-rules -->
This project uses Next.js 16 with breaking changes from standard Next.js. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Backend Directory Rule

The backend top-level directory is `/apps/backend`. Allow at most one additional directory layer under `/apps/backend`: `src`. After `src`, place functional directories directly (e.g., `api`, `core`, `models`, `services`) without extra wrapper folders.