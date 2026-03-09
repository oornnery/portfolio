# Infrastructure

## Runtime Environments

The project ships with two Docker environments.

| Environment | Compose File                     | Goal                                      |
| ----------- | -------------------------------- | ----------------------------------------- |
| Development | `docker/docker-compose.yml`      | Fast feedback with reload and bind mounts |
| Production  | `docker/docker-compose.prod.yml` | Reverse proxy + hardened runtime          |

## Dockerfiles

| Dockerfile               | Use                                     |
| ------------------------ | --------------------------------------- |
| `docker/Dockerfile.dev`  | Installs all groups, enables reload     |
| `docker/Dockerfile.prod` | Installs runtime deps only (`--no-dev`) |

## Development Topology

```mermaid
flowchart LR
    C[docker compose dev] --> A[portfolio-app-dev]
    A --> U[Uvicorn --reload]
    A -. bind mount .-> Src[app/ + content/]
```

## Production Topology

```mermaid
flowchart LR
    I[Internet / Client] --> T[Traefik :${PROD_PUBLIC_HTTP_PORT:-80}]
    T --> A[portfolio-app :8000]
    A --> O[OTLP Endpoint]
    A --> W[Webhook]
    A --> S[SMTP Server]
```

## Traefik Configuration (File-Based)

Static config:

- `docker/traefik/traefik.yml`
- File provider watching `/etc/traefik/dynamic`

Dynamic config:

- `docker/traefik/dynamic/routing.yml`
- Defines routers, middlewares, and backend service

Configured routers:

- `portfolio-web` for public website traffic
- `portfolio-contact` for `POST /contact`
- Browser traces use same-origin `POST /otel/v1/traces` served by the app,
  which forwards to the OTLP HTTP collector

Configured edge controls:

- Global rate limiting
- In-flight request cap
- Body size limits per route profile
- Compression middleware

## Application Runtime Hardening (Prod)

From `docker/docker-compose.prod.yml`:

- `read_only: true`
- `tmpfs: /tmp`
- `security_opt: no-new-privileges:true`
- Internal Docker network (`portfolio-edge`) with explicit subnet `172.28.0.0/16`
- `--forwarded-allow-ips` restricted to the Docker subnet CIDR
  (prevents header spoofing)
- App is private behind Traefik
- Production compose maps `PROD_*` env vars to app-layer checks:
  `PROD_TRUSTED_HOSTS` -> `TRUSTED_HOSTS`
  `PROD_CORS_ALLOW_ORIGINS` -> `CORS_ALLOW_ORIGINS`
  `PROD_FRONTEND_TELEMETRY_ENABLED` -> `FRONTEND_TELEMETRY_ENABLED`
  `PROD_FRONTEND_TELEMETRY_OTLP_ENDPOINT` -> `FRONTEND_TELEMETRY_OTLP_ENDPOINT`
- Health check via `GET /health` endpoint

## Observability Assets

- `infra/signoz/dashboards/portfolio-unified-operations.json`
- `infra/signoz/dashboards/portfolio-backend-overview.json`
- `infra/signoz/dashboards/portfolio-frontend-telemetry.json`
- `infra/signoz/alerts/*.json`
- The unified dashboard is the main day-to-day operations view across backend,
  frontend, contact flow, and OTLP proxy health
- The backend dashboard covers traffic, latency, status breakdowns, top paths,
  contact outcomes, notification latency, and OTLP proxy health
- The frontend dashboard covers lifecycle spans, user interaction events,
  contact form client flow, top operations, and OTLP proxy health
- Alert manifests cover backend 5xx ratio, backend p95 latency, notification
  latency, contact delivery degradation, frontend error rate, frontend
  document-load latency, and OTLP proxy failures
- Runbooks: `infra/README.md` and `infra/signoz/README.md`
- `scripts/run_otel.py` maps app telemetry settings to standard `OTEL_*`
  environment variables before launching `opentelemetry-instrument`
- `uv run task run_otel` is the supported local entrypoint for auto-instrumented
  runs
- Plain `uv run opentelemetry-instrument uvicorn app.main:app ...` is also
  supported: `usercustomize.py` applies the project resource defaults early so
  auto-instrumented spans do not fall back to `unknown_service`
- Browser tracing is configured with `FRONTEND_TELEMETRY_*` settings and uses
  the same-origin OTLP proxy route `/otel/v1/traces`
- Grafana and Prometheus rule assets are no longer maintained in this repo;
  SigNoz is the supported observability target

## CI/Quality Automation

`.github/workflows/ci.yml` runs:

- `ruff format` + `rumdl fmt` + diff verification
- `ruff check`, `ty check`
- pytest suite
- API route coverage gate (`--cov-fail-under=100` for `app/api`)
- markdown checks (`rumdl check`)
- Jx catalog check

Task automation is available via Taskipy in `pyproject.toml`.
