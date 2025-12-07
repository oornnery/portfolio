# Portfolio Project Instructions

## Architecture
FastAPI + Jinja2 + HTMX portfolio with async SQLModel ORM.

```
Request → Middleware → Router → Service → SQLModel (Async) → DB
                ↓
        Jinja2 Template → HTMX Response (HTML fragments or full pages)
```

## Project Structure
```
app/
├── main.py                 # App entry, middleware, routers
├── config.py               # Settings via pydantic-settings
├── db.py                   # Engine, session factory, seed_db()
├── api/v1/endpoints/       # JSON API (prefix /api/v1)
│   ├── auth.py             # OAuth & login
│   ├── blog.py             # Posts & reactions CRUD
│   ├── comments.py         # Comments CRUD
│   └── projects.py         # Projects CRUD
├── views/                  # HTML template views
│   ├── public.py           # Public (/, /about, /blog, /projects)
│   └── admin.py            # Admin panel (/admin/*)
├── services/               # Business logic layer
│   ├── blog.py             # BlogService + GitHubBlogService
│   ├── project.py          # Projects CRUD
│   └── profile.py          # Profile management
├── models/                 # SQLModel schemas
│   ├── blog.py             # Post, Reaction, ReactionTypeEnum
│   ├── profile.py          # Profile (work_experience, education, skills as JSON)
│   ├── project.py          # Project
│   └── user.py             # User
├── core/
│   ├── deps.py             # get_current_user, get_current_user_optional
│   └── security.py         # JWT utils, password hashing
├── middleware/
│   ├── security.py         # Security headers + X-Request-ID
│   └── logging.py          # Request timing logs
├── templates/              # Jinja2 templates
│   ├── base.html           # Base layout (nav, Tailwind, HTMX)
│   ├── admin/              # Admin panel templates
│   ├── blog/               # Blog templates (list, detail)
│   ├── pages/              # Public pages (home, about, contact)
│   └── partials/           # HTMX fragments (comments, post_list)
└── static/
    ├── css/style.css       # CSS variables
    └── js/htmx.min.js
```

## Development Commands
```bash
uv run uvicorn app.main:app --reload                                    # Dev server
uv run ruff format . && uv run ruff check . --fix --unsafe-fixes && uv run ty check .  # Lint (before commits)
uv run pytest -v                                                        # Tests
docker compose -f docker/docker-compose.dev.yml up --build              # Docker dev
```

## Critical Patterns

### 1. Async DB Operations (REQUIRED)
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_session

@router.get("/items")
async def list_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Item).where(Item.active == True))
    return result.scalars().all()
```

### 2. Template Views Pattern
```python
@router.get("/page")
async def page(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    # ALL content from backend - never hardcode in templates
    return templates.TemplateResponse("pages/page.html", {
        "request": request,
        "user": user,
        "title": "Page Title",
        "items": items_from_db,
    })
```

### 3. Model Hierarchy (Base → Table → Public/Create)
```python
class PostBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)

class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class PostPublic(PostBase):
    id: uuid.UUID

class PostCreate(PostBase):
    pass
```

### 4. Auth System
- Cookie-based JWT (`access_token` cookie with Bearer scheme)
- `get_current_user_optional` → `User | None` for public pages
- `get_current_user` → `User` (raises 401 if not authenticated)
- Admin routes redirect to `/login` if unauthenticated

### 5. Profile Model (Structured JSON Fields)
```python
class Profile(ProfileBase, table=True):
    work_experience: List[dict] = Field(default=[], sa_column=Column(JSON))
    education: List[dict] = Field(default=[], sa_column=Column(JSON))
    skills: List[str] = Field(default=[], sa_column=Column(JSON))
```

## Services Layer
| Service | Purpose |
|---------|---------|
| `BlogService` | Post CRUD, reactions, filtering by category/tag/search |
| `GitHubBlogService` | Sync posts from GitHub repository (markdown files) |
| `ProfileService` | Profile CRUD with structured work/education/skills |
| `ProjectService` | Projects CRUD operations |

**Usage pattern:**
```python
service = BlogService(session)
posts = await service.get_posts(category="tech", include_drafts=False)
```

## Jinja2 Templates

### Template Inheritance
```jinja2
{# pages/about.html #}
{% extends "base.html" %}
{% block title %}About{% endblock %}
{% block content %}
    <h1>{{ profile.name }}</h1>
{% endblock %}
```

### HTMX Integration
```html
<!-- Partial update -->
<button hx-get="/api/v1/blog?category=tech" 
        hx-target="#posts-list" 
        hx-swap="innerHTML"
        hx-indicator="#loading">
    Filter
</button>
<div id="posts-list">{% include "partials/post_list.html" %}</div>

<!-- Form submission -->
<form hx-post="/api/v1/comments/{{ post.slug }}" 
      hx-target="#comments-section" 
      hx-swap="outerHTML">
```

### Template Structure
| Directory | Purpose |
|-----------|---------|
| `base.html` | Layout base (nav, Tailwind config, HTMX) |
| `admin/` | Dashboard, CRUD forms (blog_edit, profile, projects) |
| `blog/` | Blog list and detail pages |
| `pages/` | Public pages (home, about, contact, projects, login) |
| `partials/` | HTMX fragments (comments.html, post_list.html) |

### Styling (Tailwind Dark Theme)
```javascript
// Tailwind config in base.html
colors: {
    gray: {
        900: '#111111',  // Primary bg
        800: '#1a1a1a',  // Secondary bg
        700: '#2a2a2a',  // Borders
    }
}
```

**Component classes:**
- Cards: `bg-gray-900/50 p-6 rounded-lg border border-gray-800`
- Buttons: `border border-gray-800 bg-black hover:bg-gray-800 hover:text-white`
- Links: `text-gray-400 hover:text-white transition-colors`
- Tags: `text-xs text-gray-600 bg-gray-900 px-2 py-1 rounded border border-gray-800`

**CSS variables in `static/css/style.css`:**
```css
:root {
    --accent-primary: #64ffda;
    --accent-secondary: #7c3aed;
}
```

## Conventions

### Language
- **Code/names**: English
- **Comments/docs**: Portuguese (pt-BR) allowed

### Docstrings (What/Why/How)
```python
"""
Blog service for post and reaction business logic.

Why: Centraliza regras de negócio do blog em um lugar,
     permitindo reutilização entre API e views.

How: Encapsula queries, validações e transformações de dados,
     abstraindo detalhes do ORM dos routers.
"""
```

### Naming
| Element | Style | Example |
|---------|-------|---------|
| Files | snake_case | `blog_service.py` |
| Classes | PascalCase | `PostCreate` |
| Functions | snake_case | `get_session` |
| Constants | UPPER_SNAKE | `ACCESS_TOKEN_EXPIRE_MINUTES` |
| API Routes | kebab-case | `/api/v1/my-posts` |

## Database
- Dev: `sqlite+aiosqlite:///./portfolio.db`
- Prod: `postgresql+asyncpg://...`
- Auto-seeds admin on startup: `admin@example.com` / `admin123`

## Environment Variables
```
DATABASE_URL=sqlite+aiosqlite:///./portfolio.db
SECRET_KEY=your-secret-key-here
GITHUB_CLIENT_ID=     # Optional OAuth
GITHUB_CLIENT_SECRET=
ENV=development
```

## Error Handling

### HTTPException Pattern
```python
from fastapi import HTTPException, status

@router.get("/{slug}")
async def get_post(slug: str, service: BlogService = Depends(get_blog_service)):
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with slug '{slug}' not found",
        )
    if post.draft:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This post is not published yet",
        )
    return post
```

### Path Validation with Annotated
```python
from typing import Annotated
from fastapi import Path

SlugPath = Annotated[
    str,
    Path(
        description="URL-friendly post identifier",
        min_length=1,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        examples=["getting-started-fastapi"],
    ),
]

@router.get("/{slug}")
async def get_post(slug: SlugPath): ...
```

## Rate Limiting (slowapi)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/reactions/{slug}")
@limiter.limit("10/minute")  # Max 10 reactions per minute per IP
async def add_reaction(request: Request, slug: SlugPath, ...):
    ...
```

**Common limits:**
- Public reads: `100/minute`
- Writes/mutations: `10/minute`
- Auth endpoints: `5/minute`

## Middleware

### SecurityMiddleware (`middleware/security.py`)
Adds OWASP-recommended security headers + request tracing:

| Header | Purpose |
|--------|---------|
| `X-Request-ID` | UUID for log correlation |
| `X-Content-Type-Options: nosniff` | Prevent MIME sniffing |
| `X-Frame-Options: DENY` | Prevent clickjacking |
| `X-XSS-Protection: 1; mode=block` | Legacy XSS filter |
| `Referrer-Policy` | Control referrer info |
| `Content-Security-Policy` | Allow Tailwind CDN, HTMX, fonts |

**Access request ID in handlers:**
```python
@router.get("/")
async def handler(request: Request):
    request_id = request.state.request_id
```

### RequestLoggingMiddleware (`middleware/logging.py`)
Logs structured request info for observability:
- Method, path, status code
- Processing time (ms)
- Request ID for correlation
- Skips: `/health`, `/static`, `/favicon.ico`

**Middleware order in `main.py`:**
```python
# Last added = first executed
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityMiddleware)
```

