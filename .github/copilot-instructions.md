# Portfolio Project - Copilot Instructions

## Project Overview

Full-stack portfolio application with **FastAPI** backend and **React + Vite** frontend. Uses Tokyo Night color theme throughout.

> 📋 **Implementation Plans**: See `.github/prompts/` for detailed phase-by-phase implementation guides.

## Architecture

```
portfolio/
├── backend/                    # FastAPI + SQLModel + PostgreSQL (Python 3.14+, uv)
│   ├── app/
│   │   ├── api/                # API routers
│   │   │   └── blog.py         # Blog CRUD + reactions
│   │   ├── models/             # SQLModel schemas
│   │   │   └── blog.py         # Post, Reaction, Category
│   │   ├── config.py           # Pydantic Settings
│   │   ├── db.py               # Async SQLAlchemy engine
│   │   └── main.py             # FastAPI app, middleware, rate limiting
│   ├── docker/
│   │   ├── Dockerfile          # Multi-stage Chainguard build
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   └── pyproject.toml
├── frontend/                   # React 19 + TypeScript + Vite 7 + Ant Design v6
│   ├── src/
│   │   ├── components/
│   │   │   ├── blog/           # PostCard, CodeBlock, Callout, ReadingProgress
│   │   │   ├── home/           # Hero, About, Experience, Contact
│   │   │   ├── common/         # Shared components
│   │   │   └── status/         # Health status components
│   │   ├── pages/              # Route pages (Home, Blog, BlogPost, Status)
│   │   ├── hooks/              # Custom hooks (useHealthMonitor)
│   │   ├── contexts/           # React contexts
│   │   └── theme.ts            # Tokyo Night theme config
│   ├── docker/
│   │   ├── Dockerfile          # Multi-stage Chainguard + Nginx
│   │   ├── nginx.chainguard.conf
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   └── package.json
├── docker-compose.dev.yml      # Full stack development
├── docker-compose.prod.yml     # Full stack production
├── .github/
│   ├── copilot-instructions.md # This file
│   └── prompts/                # Implementation phase guides
└── .idea/PRD.md                # Project requirements document
```

### Backend (`backend/`)
- **Framework**: FastAPI with async support
- **ORM**: SQLModel with async SQLAlchemy engine
- **Database**: PostgreSQL (prod) / SQLite with aiosqlite (dev)
- **Config**: Pydantic Settings via `app/config.py` - loads from `.env`
- **Entry point**: `app/main.py` - includes lifespan handler for DB init
- **Rate Limiting**: slowapi with configurable limits per endpoint
- **Security**: SecurityHeadersMiddleware, RequestLoggingMiddleware

### Frontend (`frontend/`)
- **Stack**: React 19 + TypeScript + Vite 7 + Ant Design v6
- **State**: TanStack Query for server state, React hooks for local
- **Styling**: Ant Design with custom Tokyo Night theme (`src/theme.ts`)
- **HTTP**: Axios for API calls
- **Animations**: Framer Motion for transitions
- **Markdown**: react-markdown with remark-gfm and syntax highlighting

## Development Commands

### Backend (Python 3.14+ with uv)
```bash
cd backend

# Dependencies
uv sync                              # Install all dependencies
uv add <package>                     # Add new dependency
uv remove <package>                  # Remove dependency

# Development
uv run uvicorn app.main:app --reload # Dev server on :8000
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000  # Bind all interfaces

# Linting & Formatting (ALWAYS run before commits)
uv run ruff format .                 # Format code
uv run ruff check . --fix --unsafe-fixes  # Lint and auto-fix

# Type checking
uv run ty check .                    # Type check with ty (red-knot)

# Testing
uv run pytest -v                     # Run tests
uv run pytest -v --cov=app           # With coverage

# Docker linting
hadolint docker/Dockerfile
bunx dclint docker/ --fix
```

### Frontend (TypeScript + bun - NOT npm)
```bash
cd frontend

# Dependencies
bun install                          # Install all dependencies
bun add <package>                    # Add new dependency
bun remove <package>                 # Remove dependency

# Development
bun run dev                          # Dev server on :5173
bun run dev --host                   # Expose to network

# Linting & Formatting (ALWAYS run before commits)
bunx biome check --write --unsafe .  # Lint and format
bunx tsc --noEmit                    # Type check only
bunx tsc -b                          # Build types

# Production
bun run build                        # Production build
bun run preview                      # Preview production build

# Docker linting  
hadolint docker/Dockerfile
bunx dclint docker/ --fix
```

### Docker (Full Stack)
```bash
# Development (hot reload)
docker compose -f docker-compose.dev.yml up --build

# Production
docker compose -f docker-compose.prod.yml up -d --build

# Per-service (backend only)
cd backend && docker compose -f docker/docker-compose.dev.yml up --build

# Per-service (frontend only)
cd frontend && docker compose -f docker/docker-compose.dev.yml up --build

# Logs
docker compose -f docker-compose.dev.yml logs -f backend
docker compose -f docker-compose.dev.yml logs -f frontend
```

## Key Patterns & Conventions

### Backend Patterns
- **Settings singleton**: Use `from app.config import settings` - never hardcode config values
- **Async DB sessions**: Use `get_session()` generator from `app/db.py`
- **API responses**: Return structured JSON with `status`, `type`, `message` for errors
- **Middleware order**: CORS first, then TrustedHostMiddleware, then custom middlewares
- **Rate limiting**: Use `@limiter.limit()` decorator on endpoints (slowapi)
- **Logging**: Use `structlog` or Python's `logging` - never `print()`

#### SQLModel Schema Rules (CRITICAL)
```python
# ✅ CORRECT - json_schema_extra at class level with model_config
from pydantic import ConfigDict

class PostBase(SQLModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"title": "My Post"}}
    )
    title: str = Field(min_length=1, description="Post title")

# ❌ WRONG - json_schema_extra inside Field() causes runtime errors!
class PostBase(SQLModel):
    title: str = Field(json_schema_extra={"example": "My Post"})  # ERROR!
```

#### Common Backend Gotchas
- Use `datetime.utcnow` for timestamps (not `datetime.now`)
- Always use `async def` for route handlers
- Use `UUID` (not `int`) for primary keys
- Validate slugs with regex: `^[a-z0-9]+(?:-[a-z0-9]+)*$`

### Frontend Patterns
- **Color system**: Always use Tokyo Night palette from `src/theme.ts` - supports `light`/`dark` variants
- **Component props**: Use Ant Design's ConfigProvider with custom theme tokens
- **Custom hooks**: Place in `src/hooks/` - see `useHealthMonitor.ts` for pattern
- **Animations**: Use Framer Motion for complex animations
- **State management**: TanStack Query for server state, React hooks for local state
- **HTTP client**: Use Axios with base URL from env
- **Routing**: React Router v6 with nested routes

#### Component Structure
```typescript
// Recommended component structure
src/components/
├── blog/          # Blog-specific components
├── home/          # Home page sections
├── projects/      # Project components
├── common/        # Shared/reusable components
├── layout/        # Layout components (Navbar, Footer)
└── auth/          # Authentication components
```

#### Ant Design Theme Usage
```typescript
import { theme } from 'antd';

// Access theme tokens in components
const { token } = theme.useToken();
// Use: token.colorPrimary, token.colorBgContainer, etc.
```

### Tokyo Night Colors Reference
```typescript
// Dark mode
bg: "#1a1b26", cardBg: "#16161e", text: "#c0caf5", border: "#292e42"
success: "#9ece6a", error: "#f7768e", accent: "#7aa2f7"

// Light mode  
bg: "#d5d6db", cardBg: "#e9e9ed", text: "#33467c", border: "#9699a3"
success: "#2d7a6e", error: "#c73866", accent: "#2e7de9"
```

## API Contract

Backend: `http://localhost:8000` | Frontend: `http://localhost:5173`

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root check `{"message": "OK"}` |
| GET | `/health` | Health check (version, platform, timestamp) |
| GET | `/ping` | Simple ping |
| GET | `/version` | Version info |
| GET | `/docs` | Swagger UI (dev only, disabled in production) |

### Blog API (`/api/blog`)
| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| GET | `/posts` | 60/min | List posts (filters: category, tag, lang, draft) |
| GET | `/posts/{slug}` | 60/min | Get post by slug (auto-increments views) |
| POST | `/posts` | 10/min | Create new post |
| PUT | `/posts/{slug}` | 10/min | Update post |
| DELETE | `/posts/{slug}` | 10/min | Delete post |
| GET | `/posts/{slug}/reactions` | 60/min | Get reactions |
| POST | `/posts/{slug}/react` | 30/min | Add reaction |
| GET | `/categories` | 60/min | List categories with counts |
| GET | `/tags` | 60/min | List tags with counts |
| GET | `/stats` | 30/min | Blog statistics |

### Rate Limits
- **Global**: 100 requests/minute per IP
- **Read endpoints**: 60/minute
- **Write endpoints**: 10/minute
- **Reactions**: 30/minute

### Frontend Health
- Static file: `/health.json` in `public/`

## Environment Variables

### Backend `.env`
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=portfolio_db
ENV=development  # production disables /docs
```

### Frontend `.env`
Standard Vite env vars with `VITE_` prefix

## Important Considerations

1. **Ant Design v6**: Uses ConfigProvider with algorithm for theming
2. **Async everywhere**: Backend is fully async - use `async def` and `await`
3. **CORS origins**: Configured for localhost:5173, :5174, and :3000 - update for production
4. **DB migrations**: Currently uses `create_all` on startup - Alembic needed for prod
5. **Theme state**: Managed manually in `App.tsx`, persisted to localStorage
6. **Package manager**: Use `bun` for frontend, `uv` for backend
7. **Fish shell**: No heredocs support - use `printf` or file edit tools instead

## Docker Setup

### Images (Chainguard - Zero CVE)
| Purpose | Image |
|---------|-------|
| Python Dev | `cgr.dev/chainguard/python:latest-dev` |
| Python Prod | `cgr.dev/chainguard/python:latest` |
| Node.js Dev | `cgr.dev/chainguard/node:latest-dev` |
| Nginx Prod | `cgr.dev/chainguard/nginx:latest` |
| PostgreSQL | `cgr.dev/chainguard/postgres:16` |

### Port Bindings
| Service | Dev | Prod | Container |
|---------|-----|------|----------|
| Frontend | 127.0.0.1:5173 | 0.0.0.0:80 | 5173/8080 |
| Backend | 127.0.0.1:8000 | 0.0.0.0:8000 | 8000 |
| PostgreSQL | 127.0.0.1:5432 | - | 5432 |

### Running with Docker
```bash
# Full stack development
docker compose -f docker-compose.dev.yml up --build

# Full stack production
docker compose -f docker-compose.prod.yml up -d --build

# Per-service
cd backend && docker compose -f docker/docker-compose.dev.yml up --build
cd frontend && docker compose -f docker/docker-compose.dev.yml up --build
```

### Chainguard Notes
- Images are updated daily with security patches
- Non-root by default (nginx runs on port 8080)
- No shell in production images - use `-dev` variants for debugging
- Health checks use Python (no curl/wget available)
