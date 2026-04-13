<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Backend Directory Rule

The backend top-level directory for this project is `/apps/backend`.
Allow at most one additional directory layer under `/apps/backend`: `src` (`/apps/backend/src`).
After `src`, place real functional directories directly (for example: `api`, `core`, `models`, `services`) instead of extra wrapper folders like `hello_wiki_backend`.
Keep only necessary top-level files and folders in `/apps/backend` (for example: `pyproject.toml`, lock files, README, scripts, and workspace/runtime data).
Do not introduce unnecessary nesting beyond this (for example: duplicated `src/app/...` or multi-layer wrapper directories with no clear value).
