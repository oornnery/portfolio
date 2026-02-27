# Docker Setup

This directory contains Docker assets for both local development and
production deployment:

- `Dockerfile.dev`
- `Dockerfile.prod`
- `docker-compose.yml`
- `docker-compose.prod.yml`

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
- Runs with multiple workers (`--workers 2`).
- Enables proxy headers for reverse-proxy deployment.
- Applies container hardening:
  - read-only filesystem
  - `tmpfs` for `/tmp`
  - `no-new-privileges`
- Defaults to `DEBUG=false` and telemetry enabled.

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
