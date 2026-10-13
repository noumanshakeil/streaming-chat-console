# Deployment — Streaming Chat Console

## Local

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Container

```bash
docker compose up --build -d
curl -fsS http://127.0.0.1:8000/health
```

## Production notes

- Set `APP_ENV=production` and `DEBUG=false` for JSON logs.
- Mount a persistent volume for `./data` (SQLite file).
- Put a reverse proxy (Caddy/Nginx) in front for TLS.
- Switch `DATABASE_URL` to Postgres (`postgresql+asyncpg://...`) when concurrency grows.
- Keep `LLM_MODE=mock` in CI; use secrets for OpenAI keys in staging/prod.
