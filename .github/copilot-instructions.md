# Portfolio Project - Copilot Instructions

## Project Overview

Minimalist full-stack portfolio application with **FastAPI** backend and **Jinja2 + HTMX** frontend. Uses a custom Space/Night color theme.

> 📋 **Implementation Plans**: See `.github/prompts/` for detailed phase-by-phase implementation guides.

## Architecture

```
portfolio/
├── app/                        # Application Source
│   ├── api/                    # API routers (HTMX/JSON)
│   │   ├── auth.py             # Authentication
│   │   ├── blog.py             # Blog endpoints
│   │   ├── comments.py         # Comments endpoints
│   │   └── projects.py         # Projects endpoints
│   ├── core/                   # Core functionality
│   │   ├── deps.py             # Dependencies
│   │   └── security.py         # Security utils
│   ├── models/                 # SQLModel schemas
│   │   ├── blog.py             # Post, Category
│   │   ├── comment.py          # Comment
│   │   ├── project.py          # Project
│   │   └── user.py             # User
│   ├── services/               # Business logic
│   ├── static/                 # Static assets
│   │   ├── css/                # Custom CSS
│   │   ├── img/                # Images
│   │   └── js/                 # HTMX and scripts
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html           # Base layout
│   │   ├── blog/               # Blog templates
│   │   └── pages/              # Page templates
│   ├── config.py               # Pydantic Settings
│   ├── db.py                   # Async SQLAlchemy engine
│   ├── main.py                 # FastAPI app entry point
│   └── views.py                # Frontend page routes
├── docker/                     # Docker configuration
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
├── pyproject.toml              # Python dependencies (uv)
└── .github/
    ├── copilot-instructions.md # This file
    └── prompts/                # Implementation phase guides
```

### Stack
- **Backend**: FastAPI (Python 3.14+)
- **Frontend**: Jinja2 Templates + HTMX
- **Database**: PostgreSQL (prod) / SQLite (dev)
- **ORM**: SQLModel (Async SQLAlchemy)
- **Styling**: Custom CSS with Variables (Minimalist)
- **Package Manager**: `uv`

## Development Commands

### Python (uv)
```bash
# Dependencies
uv sync                              # Install all dependencies
uv add <package>                     # Add new dependency
uv remove <package>                  # Remove dependency

# Development
uv run uvicorn app.main:app --reload # Dev server on :8000

# Linting & Formatting (ALWAYS run before commits)
uv run ruff format .                 # Format code
uv run ruff check . --fix --unsafe-fixes  # Lint and auto-fix

# Type checking
uv run ty check .                    # Type check with ty (red-knot)

# Testing
uv run pytest -v                     # Run tests
```

### Docker
```bash
# Development (hot reload)
docker compose -f docker/docker-compose.dev.yml up --build

# Production
docker compose -f docker/docker-compose.prod.yml up -d --build
```

## Key Patterns & Conventions

### Backend Patterns
- **Async everywhere**: Use `async def` for all route handlers.
- **Dependency Injection**: Use `Depends()` for DB sessions and services.
- **HTMX Integration**: Return `templates.TemplateResponse` for page loads and partials for HTMX requests.
- **Settings**: Use `app.config.settings`.

### Frontend Patterns (Jinja2 + HTMX)
- **Base Layout**: Extend `base.html` for all pages.
- **HTMX**: Use `hx-get`, `hx-post`, `hx-target`, `hx-swap` for dynamic interactions.
- **Partials**: Create small template partials for HTMX responses (e.g., comments list, search results).
- **CSS Variables**: Use the defined root variables for colors.

### Space/Night Theme Colors
```css
:root {
    /* Backgrounds */
    --bg-primary: #0a0e27;
    --bg-secondary: #141b33;
    --bg-tertiary: #1a2236;
    --surface: #1e2940;
    
    /* Text */
    --text-primary: #e6e8f0;
    --text-secondary: #a8b2d1;
    --text-muted: #6b7a99;
    
    /* Accents */
    --accent-primary: #64ffda;   /* Teal/Cyan */
    --accent-secondary: #7c3aed; /* Purple */
    --accent-pink: #f472b6;
    --accent-blue: #60a5fa;
    
    /* UI Elements */
    --border: #2d3a5a;
}
```

## Environment Variables

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=portfolio_db
ENV=development
```

## Important Considerations

1. **Minimalism**: Keep the UI clean and simple. Focus on content and typography.
2. **HTMX**: Prefer server-side rendering with HTMX over complex client-side JS.
3. **Security**: Ensure all forms have CSRF protection (if applicable) and proper validation.
4. **Performance**: Use `uv` for fast dependency management.

