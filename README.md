# Portfolio (FastAPI + Jx)

Server-side portfolio built with FastAPI, Jx components, markdown content,
and a service-driven backend architecture.

## Documentation

Detailed technical documentation lives in [docs/README.md](docs/README.md):

- Architecture: [docs/architecture.md](docs/architecture.md)
- Backend: [docs/backend.md](docs/backend.md)
- Frontend: [docs/frontend.md](docs/frontend.md)
- Infrastructure: [docs/infrastructure.md](docs/infrastructure.md)
- Security: [docs/security.md](docs/security.md)
- Design system: [docs/design-system.md](docs/design-system.md)
- Figma tokens: [docs/figma-tokens.md](docs/figma-tokens.md)

## Highlights

- FastAPI app factory with thin routers, orchestrator services, and dependency injection.
- Pure ASGI middleware stack (security headers, body limits, tracing).
- SSR HTML rendering with Jx + Jinja component catalog.
- Markdown-driven content model with TTL-cached nh3 sanitization.
- Contact flow with CSRF, strict validation, rate limiting,
  and decoupled notifications (webhook + SMTP).
- Analytics ingestion endpoint with allowlist and telemetry integration.
- Health check endpoint for container probes.
- OpenTelemetry traces, metrics, and logs export.

## Main Routes

| Method | Path                      | Purpose             |
| ------ | ------------------------- | ------------------- |
| GET    | `/`                       | Home                |
| GET    | `/about`                  | About               |
| GET    | `/projects`               | Projects list       |
| GET    | `/projects/{slug}`        | Project detail      |
| GET    | `/contact`                | Contact page        |
| POST   | `/contact`                | Contact submission  |
| POST   | `/api/v1/analytics/track` | Analytics ingestion |
| GET    | `/health`                 | Health check        |

## Tech Stack

- Backend: FastAPI, Uvicorn, Pydantic v2, SlowAPI, HTTPX
- Rendering: Jx, Jinja2, Tailwind CSS, custom CSS, vanilla JS
- Content: Markdown, PyYAML, nh3, cachetools
- Observability: OpenTelemetry (OTLP)
- Quality: Ruff, ty, pytest, rumdl, Taskipy

## Quick Start (Local)

1. Prepare env:

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
uv sync
```

3. Run app:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Open:

- <http://localhost:8000>

## Quality Commands

```bash
uv run ruff format .
uv run ruff check app tests app/static/js
uv run ty check app
uv run pytest -q
uv run rumdl check .
DEBUG=true PYTHONPATH=. uv run jx check app/rendering/catalog.py:catalog
```

Task aliases are available in `pyproject.toml` (`task check`, `task ci`, etc.).

## Docker

Development:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up --build -d
```

Production:

```bash
docker compose --env-file .env -f docker/docker-compose.prod.yml up --build -d
```

More details: [docker/README.md](docker/README.md).

## Security and Observability Notes

- Security controls exist at both edge (Traefik) and app middleware levels.
- Request and route limits are applied globally and for critical endpoints.
- OTLP export supports local and cloud backends (including SigNoz).
- Observability runbook: [infra/README.md](infra/README.md).
