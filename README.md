# FastAPI + UV + PostgreSQL Template

This template provides a robust backend setup using **FastAPI** for the API layer, **UV** for blazing fast package management, **SQLModel** for ORM/database interactions, and **PostgreSQL** running in Docker.

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern, fast (high-performance) web framework for building APIs with Python based on standard Python type hints.
- **[UV](https://github.com/astral-sh/uv)**: An extremely fast Python package installer and resolver, written in Rust.
- **[SQLModel](https://sqlmodel.tiangolo.com/)**: SQL databases in Python, designed to simplify interacting with SQL databases in FastAPI applications.
- **[PostgreSQL](https://www.postgresql.org/)**: The World's Most Advanced Open Source Relational Database.
- **[Docker Compose](https://docs.docker.com/compose/)**: Tool for defining and running multi-container Docker applications.

## Project Structure

```

backend/
├── app/
│   ├── core/          \# App configuration (env vars, settings)
│   ├── db.py          \# Database connection and session management
│   └── main.py        \# App entrypoint and CORS config
├── docker/            \# Docker configuration files
│   ├── Dockerfile     \# Production-ready Dockerfile
│   └── docker-compose.yml
├── .env               \# Environment variables (Not committed)
├── pyproject.toml     \# Project dependencies
└── uv.lock            \# Locked dependencies

```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 1. Environment Setup

Create a `.env` file in the `backend/` root directory:

```

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=portfolio_db

# For local development (outside Docker):

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db

# For Docker container (inside Docker):

# DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/portfolio_db

```

### 2. Running Locally (Development)

Start the database container and then run the API locally for faster debugging:

```


# 1. Start PostgreSQL container

docker compose -f docker/docker-compose.yml up -d db

# 2. Install dependencies

uv sync

# 3. Run the server with hot-reload

uv run uvicorn app.main:app --reload

```
The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`.

### 3. Running with Docker (Full Stack)

To run the entire backend infrastructure (API + DB) inside containers:

```

cd backend
docker compose -f docker/docker-compose.yml up --build

```

## Development Workflows

### Adding Dependencies

Using `uv` is much faster than pip. To add a new library:

```

uv add <package_name>

# Example: uv add pydantic

```

### Database Migrations

Currently, the project uses `SQLModel.metadata.create_all` on startup for simplicity. For production workflows, integrating **Alembic** is recommended.

### Linting & Formatting

(Recommended configuration - add to `pyproject.toml` if needed)
- **Ruff**: An extremely fast Python linter, written in Rust.
```

uv add --dev ruff
uv run ruff check .

```

