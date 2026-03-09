# Docker Setup

This directory contains Docker assets for both local development and
production deployment:

- `Dockerfile.dev`
- `Dockerfile.prod`
- `docker-compose.yml`
- `docker-compose.prod.yml`
- `traefik/traefik.yml` (static Traefik config)
- `traefik/dynamic/*.yml` (dynamic Traefik config)

## Requirements

- Docker Engine 24+
- Docker Compose v2 (`docker compose`)

## Run (development)

Use the root `.env` file (copy from `.env.example` if needed):

```bash
cp .env.example .env
```

From the project root:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up --build -d
```

Check status:

```bash
docker compose -f docker/docker-compose.yml ps
```

View logs:

```bash
docker compose -f docker/docker-compose.yml logs -f app
```

Stop and remove:

```bash
docker compose --env-file .env -f docker/docker-compose.yml down
```

## Run (production)

Use the same root `.env` file and adjust production values as needed:

```bash
cp .env.example .env
```

From the project root:

```bash
docker compose --env-file .env -f docker/docker-compose.prod.yml up --build -d
```

Recommended production values in `.env`:

```bash
PROD_BASE_URL=https://example.com
PROD_TRUSTED_HOSTS=example.com,www.example.com
PROD_CORS_ALLOW_ORIGINS=https://example.com
PROD_OTEL_SERVICE_NAME=site-backend
PROD_OTEL_RESOURCE_ATTRIBUTES=service.namespace=site,deployment.environment=production
PROD_OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:4317
PROD_OTEL_EXPORTER_OTLP_INSECURE=true
PROD_OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
PROD_FRONTEND_TELEMETRY_ENABLED=true
PROD_FRONTEND_TELEMETRY_OTLP_ENDPOINT=
PROD_PUBLIC_HTTP_PORT=80
```

Stop and remove:

```bash
docker compose --env-file .env -f docker/docker-compose.prod.yml down
```

## Publish to GHCR

GitHub Actions publishes the production image from `docker/Dockerfile.prod` to:

- `ghcr.io/oornnery/site`

Workflow file:

- `.github/workflows/docker-publish.yml`

Triggers:

- push to `master`
- push tags matching `v*`
- manual `workflow_dispatch`

Published tags include:

- `latest` on the default branch
- branch tag (`master`)
- git tag names (`v1.2.3`, etc.)
- `sha-<commit>`

## Port and URL

- Exposed port: `${PROD_PUBLIC_HTTP_PORT:-80}` -> container `8000`
- Local URL (with defaults): `http://localhost`
- In production compose, Traefik is the public entrypoint and the app container
  is private to the internal Docker network.

## Main environment variables

Defined in compose files:

- Base values come from root `.env` (`env_file: ../.env`).
- Compose files may override selected runtime values per environment.

## Environment differences

### Development (`docker-compose.yml`)

- Uses `Dockerfile.dev`.
- Builds tagged image `site-app-dev:latest`.
- Installs all dependency groups (`--all-groups`).
- Runs `opentelemetry-instrument uvicorn --reload` for code/template/content
  changes.
- Mounts source folders as bind volumes:
  - `app`, `content`
- Defaults to `DEBUG=true`.

### Production (`docker-compose.prod.yml`)

- Uses `Dockerfile.prod`.
- Builds tagged image `site-app:latest`.
- Installs only runtime dependencies (`--no-dev`).
- Runs `opentelemetry-instrument uvicorn`.
- Runs behind Traefik (`traefik:v3`) as reverse proxy on
  `${PROD_PUBLIC_HTTP_PORT:-80}`.
- App container is not exposed directly; requests flow through Traefik.
- Traefik static config is loaded from `docker/traefik/traefik.yml`.
- Traefik dynamic config is loaded from `docker/traefik/dynamic/`.
- Runs with multiple workers (`--workers 2`).
- Enables proxy headers for reverse-proxy deployment.
- Enables trusted forwarded headers in the app (`TRUST_FORWARDED_IP_HEADERS=true`).
- Requires explicit production host/origin environment values
  (`PROD_BASE_URL`, `PROD_TRUSTED_HOSTS`, `PROD_CORS_ALLOW_ORIGINS`).
- Frontend OTLP export is configured with `PROD_FRONTEND_TELEMETRY_*`
  variables and uses the same-origin proxy route `POST /otel/v1/traces`.
- Backend OTLP export is configured with `PROD_OTEL_*` variables passed
  directly to the CLI-managed SDK.
- Both dev and prod compose files map `host.docker.internal` to the Docker host
  so the app container can reach a collector published on host ports `4317/4318`.
- Applies container hardening:
  - read-only filesystem
  - `tmpfs` for `/tmp`
  - `no-new-privileges`
- Defaults to `DEBUG=false` and telemetry enabled.

## Traefik route security

`docker/traefik/dynamic/routing.yml` defines two Traefik routers:

- `site-web`: serves all regular routes.
- `site-contact`: handles only `POST /contact` with stricter body-size cap.

Main middlewares in Traefik dynamic config:

- `site-rate-limit-global`: global edge rate limit.
- `site-body-limit-web`: global request body cap.
- `site-body-limit-contact`: stricter cap for contact form submission.
- `site-inflight-global`: caps concurrent in-flight requests.
- `site-compress`: response compression.

To customize host matching, edit:

- `docker/traefik/dynamic/routing.yml`

For stricter host filtering at edge, add `Host(...)` matchers in each router
rule in `routing.yml` and keep them aligned with `TRUSTED_HOSTS`.

## Traefik config files

- Static config:
  `docker/traefik/traefik.yml`
- Dynamic routing and middleware config:
  `docker/traefik/dynamic/routing.yml`

## Notes

- The service runs `opentelemetry-instrument uvicorn app.main:app`.
- The healthcheck calls `GET /health` from inside the container.
- The build context is the project root (`..`), using
  `docker/Dockerfile.dev` or `docker/Dockerfile.prod`.
- The GHCR workflow publishes only the production image, not the dev image.

## Refs

- Docker Compose file reference:
  <https://docs.docker.com/reference/compose-file/>
- Dockerfile reference:
  <https://docs.docker.com/reference/dockerfile/>
- FastAPI deployment (Docker):
  <https://fastapi.tiangolo.com/deployment/docker/>
