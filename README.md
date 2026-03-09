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
- Browser telemetry via OpenTelemetry JS plus backend OTLP export.
- Health check endpoint for container probes.
- OpenTelemetry traces, metrics, and logs export.

## Main Routes

| Method | Path                      | Purpose             |
| ------ | ------------------------- | ------------------- |
| GET    | `/`                       | Home                |
| GET    | `/about`                  | About               |
| GET    | `/projects`               | Projects list       |
| GET    | `/projects/{slug}`        | Project detail      |
| GET    | `/blog`                   | Blog home           |
| GET    | `/blog/posts`             | Blog posts list     |
| GET    | `/blog/posts/{slug}`      | Blog post detail    |
| GET    | `/blog/tags`              | Blog tags           |
| GET    | `/blog/tags/{tag}`        | Blog tag detail     |
| GET    | `/blog/feed.xml`          | Blog RSS feed       |
| GET    | `/about/resume.md`        | Resume download     |
| GET    | `/contact`                | Contact page        |
| POST   | `/contact`                | Contact submission  |
| POST   | `/otel/v1/traces`         | Frontend OTLP proxy |
| GET    | `/health`                 | Health check        |

## Tech Stack

- Backend: FastAPI, Uvicorn, Pydantic v2, SlowAPI, HTTPX
- Rendering: Jx, Jinja2, Tailwind CSS, custom CSS
- Frontend JS: Alpine.js (CSP-safe), Stimulus, htmx
- Build: esbuild (JS bundle), Tailwind CLI (CSS)
- Content: Markdown, PyYAML, Pygments, nh3, cachetools
- Observability: OpenTelemetry (OTLP), Rich (logging)
- Quality: Ruff, ty, pytest, rumdl, Taskipy

## Quick Start (Local)

1. Prepare env:

```bash
cp .env.example .env
```

1. Install dependencies:

```bash
uv sync && npm install
```

1. Build assets:

```bash
uv run task build
```

1. Run app:

```bash
uv run task run
```

Auto-instrumented runtime with OpenTelemetry distro:

```bash
uv run task run_otel
```

1. Open:

- <http://localhost:8000>

## Quality Commands

```bash
uv run ruff format .
uv run ruff check app tests app/static/js
uv run ty check app
uv run pytest -q
uv run rumdl check .
DEBUG=true PYTHONPATH=. uv run jx check app/catalog.py:catalog
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
- Frontend telemetry uses same-origin `POST /otel/v1/traces`, and the app
  forwards OTLP HTTP payloads to the configured collector.
- `uv run task run` uses the app-managed telemetry bootstrap.
- `uv run task run_otel` is just a convenience alias for
  `uv run opentelemetry-instrument uvicorn app.main:app ...`.
- `usercustomize.py` maps the project's `.env` telemetry settings into
  standard `OTEL_*` variables early in process startup, so direct
  auto-instrumented runs pick up the same collector, headers, and
  `service.name` defaults as the app-managed bootstrap.
- Importable SigNoz dashboards and alert manifests live under
  [infra/signoz](infra/signoz).
- Observability runbook: [infra/README.md](infra/README.md).
