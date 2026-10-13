            # Streaming Chat Console

            Token-streaming chat console with durable sessions, system prompts, message history, and SSE-style streaming — mock/OpenAI/Ollama providers behind one service boundary.

            ![CI](https://img.shields.io/badge/CI-pytest%20%7C%20ruff%20%7C%20mypy-22c55e)
            ![Python](https://img.shields.io/badge/python-3.11%2B-3b82f6)
            ![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20SQLAlchemy%20%7C%20Jinja-0ea5e9)
            ![License](https://img.shields.io/badge/license-MIT-informational)

            ## Why this exists

            Thin “RAG demo” repos usually stop at a single `/ask` endpoint and a mock answer.
            This project is structured like an engineering deliverable: ingest → chunk → retrieve →
            generate → cite, with an operator UI, health checks, structured logging, Docker, and CI.

            ## Features

            - Chat sessions with persisted message history
- Named system prompts + per-session overrides
- SSE streaming endpoint (`/api/sessions/{id}/stream`)
- Mock/OpenAI/Ollama via shared LLM factory
- Operator UI + Docker/CI

            ## Architecture (high level)

            ```
            Browser / API client
                    │
                    ▼
            FastAPI (middleware + routers)
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
      Ingest     Retrieve    Answer
      (chunk)   (lexical)   (LLM + citations)
         │          │          │
         └──────────┴──────────┘
                    ▼
              SQLite (async SQLAlchemy)
            ```

            Lexical ranking ships by default so CI stays deterministic. Replace `score_chunk`
            with embedding cosine similarity (pgvector / Qdrant / OpenAI embeddings) without
            changing the API surface.

            ## Quick start

            ```bash
            python -m venv .venv
            # Windows: .venv\\Scripts\\activate
            source .venv/bin/activate
            pip install -r requirements.txt -r requirements-dev.txt
            cp .env.example .env
            uvicorn backend.main:app --reload --port 8000
            ```

            Open http://127.0.0.1:8000 — the Jinja console is the fastest way to exercise the flow.

            ## Docker

            ```bash
            docker compose up --build
            ```

            Healthcheck hits `/health`. Persist SQLite via the `./data` volume.

            ## LLM modes

            | Mode | When to use |
            |------|-------------|
            | `mock` (default) | Offline demos + pytest |
            | `openai` | Set `OPENAI_API_KEY` |
            | `ollama` | Local models via `OLLAMA_BASE_URL` |

            ## HTTP API (summary)

            - `GET/POST /api/system-prompts`
- `GET/POST /api/sessions`
- `GET /api/sessions/{id}/messages`
- `POST /api/sessions/{id}/messages`
- `POST /api/sessions/{id}/stream`

            Full reference: [docs/api.md](docs/api.md)

            ## Tests & quality gates

            ```bash
            pytest -q --cov=backend --cov-report=term-missing
            ruff check backend tests
            mypy backend --ignore-missing-imports
            ```

            GitHub Actions runs the same gate on every push to `main`.

            ## Docs

            - [Architecture](docs/architecture.md)
            - [API](docs/api.md)
            - [Deployment](docs/deployment.md)
            - [Operations runbook](docs/runbook.md)

            ## License

            MIT — see [LICENSE](LICENSE).
