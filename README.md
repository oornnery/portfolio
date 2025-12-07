# Portfolio - FastAPI + Jinja2 + HTMX

Minimalist full-stack portfolio with blog, projects, and resume management.

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)**: Async web framework with automatic OpenAPI docs
- **[Jinja2](https://jinja.palletsprojects.com/)**: Server-side templating
- **[HTMX](https://htmx.org/)**: Dynamic interactions without JavaScript
- **[SQLModel](https://sqlmodel.tiangolo.com/)**: Async ORM built on SQLAlchemy + Pydantic
- **[Tailwind CSS](https://tailwindcss.com/)**: Utility-first CSS (via CDN)
- **[UV](https://github.com/astral-sh/uv)**: Fast Python package manager (Rust)
- **PostgreSQL** (prod) / **SQLite** (dev)

## Project Structure

```
app/
├── main.py                 # App entry, middleware, routers
├── config.py               # Settings via pydantic-settings
├── db.py                   # Engine, session factory, seed_db()
├── api/v1/endpoints/       # JSON API (prefix /api/v1)
├── views/                  # HTML template views (public + admin)
├── services/               # Business logic layer
├── models/                 # SQLModel schemas
├── core/                   # Auth, security, dependencies
├── middleware/             # Security headers, logging
├── templates/              # Jinja2 templates
└── static/                 # CSS, JS (htmx.min.js)
```

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker (optional, for PostgreSQL)

### 1. Environment Setup

Create a `.env` file:

```bash
DATABASE_URL=sqlite+aiosqlite:///./portfolio.db  # Dev (default)
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db  # Prod
SECRET_KEY=your-secret-key-here
ENV=development
```

### 2. Running Locally

```bash
# Install dependencies
uv sync

# Run dev server with hot-reload
uv run uvicorn app.main:app --reload
```

The app will be available at `http://localhost:8000`.
- Interactive API docs: `http://localhost:8000/docs`
- Admin panel: `http://localhost:8000/admin` (login: `admin@example.com` / `admin123`)

### 3. Running with Docker

```bash
# Development
docker compose -f docker/docker-compose.dev.yml up --build

# Production
docker compose -f docker/docker-compose.prod.yml up --build
```

## Development Workflows

### Linting & Formatting (REQUIRED before commits)

```bash
uv run ruff format . && uv run ruff check . --fix --unsafe-fixes && uv run ty check .
```

### Running Tests

```bash
uv run pytest -v
```

### Adding Dependencies

```bash
uv add <package_name>
uv add --dev <dev_package>  # Dev dependencies
```

## Key Features

- **Blog**: Posts with categories, tags, reactions, comments
- **Projects**: Portfolio showcase with tech stack tags
- **Profile/Resume**: Work experience, education, skills (JSON fields)
- **Admin Panel**: CRUD for all content
- **Auth**: Cookie-based JWT with optional GitHub/Google OAuth
- **Rate Limiting**: slowapi protection on public endpoints
- **Security**: OWASP headers, CSP, request tracing

## Documentation

See [`.github/copilot-instructions.md`](.github/copilot-instructions.md) for detailed architecture, patterns, and conventions.

