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

Stop and remove:

```bash
docker compose --env-file .env -f docker/docker-compose.prod.yml down
```

## Port and URL

- Exposed port: `8000`
- Local URL: `http://localhost:8000`
- In production compose, Traefik is the public entrypoint and the app container
  is private to the internal Docker network.

## Main environment variables

Defined in compose files:

- Base values come from root `.env` (`env_file: ../.env`).
- Compose files may override selected runtime values per environment.

## Environment differences

### Development (`docker-compose.yml`)

- Uses `Dockerfile.dev`.
- Installs all dependency groups (`--all-groups`).
- Enables auto-reload (`uvicorn --reload`) for code/template/content changes.
- Mounts source folders as bind volumes:
  - `app`, `content`
- Defaults to `DEBUG=true`.

### Production (`docker-compose.prod.yml`)

- Uses `Dockerfile.prod`.
- Installs only runtime dependencies (`--no-dev`).
- Runs behind Traefik (`traefik:v3`) as reverse proxy on port `8000`.
- App container is not exposed directly; requests flow through Traefik.
- Traefik static config is loaded from `docker/traefik/traefik.yml`.
- Traefik dynamic config is loaded from `docker/traefik/dynamic/`.
- Runs with multiple workers (`--workers 2`).
- Enables proxy headers for reverse-proxy deployment.
- Enables trusted forwarded headers in the app (`TRUST_FORWARDED_IP_HEADERS=true`).
- Restricts only `POST /api/v1/analytics/track` at edge with Traefik
  `ipAllowList` middleware.
- Applies container hardening:
  - read-only filesystem
  - `tmpfs` for `/tmp`
  - `no-new-privileges`
- Defaults to `DEBUG=false` and telemetry enabled.

## Traefik route security

`docker/traefik/dynamic/routing.yml` defines three Traefik routers:

- `portfolio-web`: serves all regular routes.
- `portfolio-contact`: handles only `POST /contact` with stricter body-size cap.
- `portfolio-analytics`: matches only
  `POST /api/v1/analytics/track` and applies IP allowlist.

Main middlewares in Traefik dynamic config:

- `portfolio-rate-limit-global`: global edge rate limit.
- `portfolio-analytics-rate-limit`: tighter limit only for analytics ingestion.
- `portfolio-body-limit-web`: global request body cap.
- `portfolio-body-limit-contact`: stricter cap for contact form submission.
- `portfolio-body-limit-analytics`: dedicated cap for analytics payloads.
- `portfolio-inflight-global`: caps concurrent in-flight requests.
- `portfolio-compress`: response compression.
- `portfolio-analytics-allow`: IP allowlist for analytics ingest.

To customize host matching and analytics source allowlist, edit:

- `docker/traefik/dynamic/routing.yml`

## Traefik config files

- Static config:
  `docker/traefik/traefik.yml`
- Dynamic routing and middleware config:
  `docker/traefik/dynamic/routing.yml`

## Notes

- The service runs `uvicorn app.main:app`.
- The healthcheck calls `GET /` from inside the container.
- The build context is the project root (`..`), using
  `docker/Dockerfile.dev` or `docker/Dockerfile.prod`.

## Refs

- Docker Compose file reference:
  <https://docs.docker.com/reference/compose-file/>
- Dockerfile reference:
  <https://docs.docker.com/reference/dockerfile/>
- FastAPI deployment (Docker):
  <https://fastapi.tiangolo.com/deployment/docker/>
