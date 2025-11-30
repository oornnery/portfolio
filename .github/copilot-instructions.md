# Portfolio Project - Copilot Instructions

## Overview
Minimalist full-stack portfolio with **FastAPI + Jinja2 + HTMX**. Personal portfolio site for "Fabio Souza" with blog, projects, and resume/profile management.

## Architecture

### Core Data Flow
```
Request → Middleware → FastAPI Router → Service Layer → SQLModel (Async) → PostgreSQL/SQLite
                ↓
        Jinja2 Template → HTMX Response (HTML fragments or full pages)
```

### Project Structure
```
app/
├── main.py              # App entry point, middleware registration
├── config.py            # Settings via pydantic-settings
├── db.py                # Database engine and session
├── api/
│   ├── __init__.py      # Exports api_router
│   └── v1/              # Versioned API (JSON endpoints)
│       ├── __init__.py  # Aggregates all v1 routers
│       └── endpoints/
│           ├── auth.py      # OAuth & login
│           ├── blog.py      # Posts & reactions CRUD
│           ├── projects.py  # Projects CRUD
│           └── comments.py  # Comments CRUD
├── views/               # Template views (HTML responses)
│   ├── __init__.py      # Exports public_router, admin_router
│   ├── public.py        # Public pages (/, /about, /blog, /projects)
│   └── admin.py         # Admin panel (/admin/*)
├── models/              # SQLModel schemas + Pydantic validation
│   ├── blog.py          # Post, Reaction, Category models
│   ├── project.py       # Project model
│   ├── profile.py       # Profile model (work, education, skills)
│   ├── comment.py       # Comment model
│   └── user.py          # User model
├── services/            # Business logic layer
│   ├── auth.py          # Auth logic, JWT, OAuth
│   ├── blog.py          # BlogService + GitHubBlogService
│   ├── project.py       # Projects business logic
│   └── profile.py       # Profile management
├── middleware/          # Cross-cutting concerns
│   ├── security.py      # Security headers + X-Request-ID
│   └── logging.py       # Request logging with timing
├── core/
│   ├── deps.py          # FastAPI dependencies (get_current_user)
│   ├── security.py      # Password hashing, JWT utils
│   └── utils.py         # Form parsing utilities
├── static/              # Static assets
│   ├── css/style.css    # Custom CSS variables
│   └── js/htmx.min.js   # HTMX library
└── templates/           # Jinja2 templates
    ├── base.html        # Base layout with nav
    ├── admin/           # Admin panel templates
    ├── blog/            # Blog templates
    ├── pages/           # Public page templates
    └── partials/        # HTMX partial responses
```

### Key Directories
| Directory | Purpose |
|-----------|---------|
| `app/api/v1/endpoints/` | REST API (JSON) - prefix `/api/v1` |
| `app/views/` | Template views (HTML) - no schema |
| `app/services/` | Business logic - DB operations, validations |
| `app/middleware/` | Request/response middleware |
| `app/models/` | SQLModel schemas with Pydantic validation |
| `app/core/` | Auth, security, utilities |

### Three Layer Architecture
1. **API/Views Layer** - Routers, request handling, response formatting
2. **Service Layer** - Business logic, validations, orchestration
3. **Model Layer** - Data models, ORM, schemas

## Development Commands

```bash
# Run dev server
uv run uvicorn app.main:app --reload

# ALWAYS before commits
uv run ruff format . && uv run ruff check . --fix --unsafe-fixes

# Type checking & tests
uv run ty check .
uv run pytest -v

# Docker dev
docker compose -f docker/docker-compose.dev.yml up --build
```

## Critical Patterns

### 1. Async SQLModel Pattern (REQUIRED)
All DB operations use async sessions via `Depends(get_session)`:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_session

@router.get("/items")
async def list_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Item))
    return result.scalars().all()
```

### 2. Auth Pattern
- Cookie-based JWT (`access_token` cookie with `Bearer` scheme)
- Use `get_current_user_optional` for optional auth (returns `User | None`)
- Admin routes redirect to `/login` if not authenticated

### 3. Template Response Pattern
```python
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["settings"] = settings

@router.get("/page")
async def page(request: Request, user: User | None = Depends(get_current_user_optional)):
    # ALL text/data must come from backend - never hardcode in templates
    context = {
        "request": request,
        "user": user,
        "page_title": "About Me",
        "section_heading": "My Skills",
        "items": items_from_db,
    }
    return templates.TemplateResponse("pages/page.html", context)
```

### 4. Model Structure (SQLModel)
Models follow: `Base → Table(Base, table=True) → Public/Create schemas`
```python
class PostBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    
class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
class PostPublic(PostBase):
    id: uuid.UUID
```

## Jinja2 Templates - IMPORTANT RULES

### Use Macros to Avoid Repetition
Create reusable macros in `templates/macros/` and import them:
```jinja2
{# templates/macros/components.html #}
{% macro card(title, description, link) %}
<article class="card">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <a href="{{ link }}">{{ link_text }}</a>
</article>
{% endmacro %}

{# Usage in page template #}
{% from "macros/components.html" import card %}
{% for project in projects %}
    {{ card(project.title, project.description, project.url) }}
{% endfor %}
```

### No Hardcoded Text in Templates
❌ **WRONG** - Text hardcoded in HTML:
```html
<h1>Welcome to My Portfolio</h1>
<p>I'm a Full-stack Developer</p>
```

✅ **CORRECT** - All data from backend context:
```html
<h1>{{ page_title }}</h1>
<p>{{ hero_description }}</p>
```

### Template Structure
```
templates/
├── base.html              # Base layout (extends nothing)
├── macros/                # Reusable macro components
│   ├── components.html    # Cards, buttons, forms
│   └── forms.html         # Form field macros
├── partials/              # HTMX partial responses
├── pages/                 # Full page templates
├── admin/                 # Admin panel templates
└── blog/                  # Blog-specific templates
```

## Code Quality Standards

### Language Convention
- **Code**: All code, variable names, function names, file names, classes → **English**
- **Comments/Docs**: Can be in **Portuguese (pt-BR)** for clarity
- **Commit messages**: English preferred

```python
# ✅ CORRECT
def get_published_posts() -> list[Post]:
    """
    Retorna todos os posts publicados ordenados por data.
    
    Why: Filtra drafts para não expor conteúdo não finalizado.
    """
    pass

# ❌ WRONG
def obter_posts_publicados():  # Nome em português
    pass
```

### Documentation Requirements
Every file/module must have a docstring explaining:
1. **What** - Purpose of the module/function
2. **Why** - Reasoning behind design decisions  
3. **How** - Key implementation details if non-obvious

```python
"""
Blog API endpoints for managing posts and reactions.

Why: Separates blog logic from main views for cleaner architecture.
     Rate limiting protects against abuse on public endpoints.

How: Uses slowapi for rate limiting, SQLModel for ORM,
     returns both JSON (API clients) and HTML partials (HTMX).
"""
```

### Clean Code Principles
- **Single Responsibility**: One function/class = one job
- **Descriptive Names**: `get_published_posts()` not `get_posts2()`
- **Small Functions**: Max ~20 lines, extract helpers if larger
- **Type Hints**: All function signatures must be typed
- **No Magic Numbers**: Use constants or config values

### Naming Conventions
| Element | Style | Example |
|---------|-------|---------|
| Files/Modules | snake_case | `blog_service.py` |
| Classes | PascalCase | `PostCreate`, `UserPublic` |
| Functions/Variables | snake_case | `get_session`, `current_user` |
| Constants | UPPER_SNAKE | `ACCESS_TOKEN_EXPIRE_MINUTES` |
| API Routes | kebab-case | `/api/blog/my-posts` |

### Error Handling Pattern
```python
from fastapi import HTTPException, status

# Use specific HTTP status codes with clear messages
@router.get("/posts/{slug}")
async def get_post(slug: str, session: AsyncSession = Depends(get_session)):
    post = await session.execute(select(Post).where(Post.slug == slug))
    result = post.scalar_one_or_none()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with slug '{slug}' not found"
        )
    
    if result.draft:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This post is not published yet"
        )
    
    return result
```

## Security Best Practices

### Input Validation
- All user input validated via Pydantic models
- Use `Field(min_length=, max_length=, pattern=)` constraints
- Sanitize markdown content before rendering

### Authentication
- JWT tokens stored in HttpOnly cookies (not localStorage)
- Token expiration: 30 minutes (configurable)
- Password hashing: bcrypt via `passlib`

### SQL Injection Prevention
- Always use SQLModel/SQLAlchemy ORM - never raw SQL strings
- Parameterized queries via `select().where()`

### Rate Limiting
- Public API endpoints use `slowapi` limiter
- See `app/api/v1/endpoints/blog.py` for implementation example

### Headers & CORS
- Security headers via `SecurityHeadersMiddleware`:
  - X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
  - Content-Security-Policy (configurable)
- Configure `ALLOW_ORIGINS` in settings for production
- CSRF tokens for forms (recommended)

## Middleware Layer
Custom middlewares in `app/middleware/`:

| Middleware | Purpose |
|------------|---------|
| `SecurityMiddleware` | Security headers (CSP, X-Frame-Options) + X-Request-ID for tracing |
| `RequestLoggingMiddleware` | Request logging with timing |

## Database Seeding
`app/db.py:seed_db()` auto-creates admin user on startup:
- Email: `admin@example.com`, Password: `admin123`

---

## Frontend Architecture

### Tech Stack
- **Tailwind CSS** via CDN with custom dark theme config
- **HTMX** for dynamic interactions without JavaScript
- **Jinja2** for server-side templating
- **Inter** font from Google Fonts

### Template Structure
```
templates/
├── base.html              # Base layout - nav, head, scripts
├── admin/                 # Admin panel
│   ├── dashboard.html
│   ├── blog_list.html
│   ├── blog_edit.html
│   ├── projects_list.html
│   ├── project_edit.html
│   └── profile.html
├── blog/
│   ├── list.html          # Blog listing
│   └── detail.html        # Single post view
├── pages/
│   ├── home.html          # Landing page with hero
│   ├── about.html         # Resume/CV page
│   ├── projects.html      # Projects listing
│   ├── project_detail.html
│   ├── contact.html
│   └── login.html
└── partials/              # HTMX fragments
    ├── comments.html
    └── post_list.html
```

### Current Issues to Fix ⚠️

#### 1. Hardcoded Text in Templates
**Problem**: Templates have hardcoded Portuguese/English text that should come from backend.

❌ **Current** (`home.html`):
```html
<h1 class="text-2xl font-bold text-white">Fabio Souza</h1>
<p>Experienced telecommunications professional...</p>
```

✅ **Should be**:
```html
<h1 class="text-2xl font-bold text-white">{{ profile.name }}</h1>
<p>{{ profile.short_bio }}</p>
```

#### 2. Missing Macros for Reusable Components
**Problem**: Repeated HTML patterns without macros.

**Create** `templates/macros/` folder with:
- `components.html` - Cards, buttons, badges
- `forms.html` - Form fields, inputs
- `icons.html` - SVG icon macros

**Example macro**:
```jinja2
{# macros/components.html #}
{% macro social_button(href, label, icon_name) %}
<a href="{{ href }}" aria-label="{{ label }}" target="_blank" rel="noopener noreferrer"
   class="inline-flex items-center justify-center size-8 border border-gray-800 
          bg-black hover:bg-gray-800 hover:text-white rounded-md transition-colors">
    {{ caller() if caller else '' }}
</a>
{% endmacro %}

{% macro project_card(project) %}
<a href="{{ project.demo_url or project.github_url or '#' }}" 
   class="block group bg-gray-900/50 p-6 rounded-lg border border-gray-800 
          hover:border-gray-700 transition-colors">
    <h3 class="text-white font-medium group-hover:text-blue-400">{{ project.title }}</h3>
    <p class="text-sm text-gray-500">{{ project.description }}</p>
    <div class="flex gap-2 mt-2">
        {% for tech in project.tech_stack %}
        <span class="text-xs text-gray-600 bg-gray-900 px-2 py-1 rounded border border-gray-800">
            {{ tech }}
        </span>
        {% endfor %}
    </div>
</a>
{% endmacro %}
```

#### 3. API Route Updates
**Problem**: Some templates reference old API routes.

| Old Route | New Route |
|-----------|-----------|
| `/api/auth/*` | `/api/v1/auth/*` |
| `/api/blog/*` | `/api/v1/blog/*` |
| `/api/projects/*` | `/api/v1/projects/*` |
| `/api/comments/*` | `/api/v1/comments/*` |

**Files to update**:
- `base.html` - Logout link
- Any HTMX `hx-post`, `hx-get` attributes

#### 4. Profile Data Not Dynamic
**Problem**: `home.html` has static profile data instead of using `{{ profile }}`.

**Fix**: Pass profile from views and use template variables:
```python
# views/public.py
@router.get("/")
async def home(request: Request, session: AsyncSession = Depends(get_session)):
    profile = await session.execute(select(Profile).limit(1))
    return templates.TemplateResponse("pages/home.html", {
        "request": request,
        "profile": profile.scalar_one_or_none(),
        # ...
    })
```

### Styling Guidelines

#### Dark Theme Colors (Tailwind Config)
```javascript
colors: {
    gray: {
        900: '#111111',  // Primary background
        800: '#1a1a1a',  // Secondary background
        700: '#2a2a2a',  // Borders, cards
        600: '#444444',
        500: '#666666',
        400: '#888888',  // Muted text
        300: '#aaaaaa',
        200: '#cccccc',
        100: '#eeeeee',
    }
}
```

#### CSS Variables (`static/css/style.css`)
```css
:root {
    --accent-primary: #64ffda;    /* Teal accent */
    --accent-secondary: #7c3aed;  /* Purple accent */
    --accent-glow: #a78bfa;
    --bg-primary: #0a0e27;
    --bg-secondary: #141b33;
}
```

#### Component Patterns
- **Buttons**: `border border-gray-800 bg-black hover:bg-gray-800`
- **Cards**: `bg-gray-900/50 p-6 rounded-lg border border-gray-800`
- **Links**: `text-gray-400 hover:text-white transition-colors`
- **Tags/Badges**: `text-xs text-gray-600 bg-gray-900 px-2 py-1 rounded`

### HTMX Patterns

#### Partial Updates
```html
<!-- Trigger -->
<button hx-get="/api/v1/blog?category=tech" 
        hx-target="#posts-list" 
        hx-swap="innerHTML">
    Filter by Tech
</button>

<!-- Target -->
<div id="posts-list">
    {% include "partials/post_list.html" %}
</div>
```

#### Form Submission
```html
<form hx-post="/api/v1/comments/{{ post.slug }}" 
      hx-target="#comments-section" 
      hx-swap="outerHTML">
    <textarea name="content" required></textarea>
    <button type="submit">Post Comment</button>
</form>
```

### Recommended Frontend Tasks

1. **Create macros folder** with reusable components
2. **Update API routes** from `/api/` to `/api/v1/`
3. **Remove hardcoded text** - use `{{ profile.* }}` variables
4. **Add loading states** with `hx-indicator`
5. **Improve accessibility** - ARIA labels, focus states
6. **Create icon macro** to centralize SVG icons

---

## Styling (Dark Theme)
Templates use **Tailwind CDN** with custom dark palette:
- Background: `gray-900` (#111111), `gray-800` (#1a1a1a)
- Accents: Teal (`#64ffda`), Purple (`#7c3aed`)
- CSS variables defined in `app/static/css/style.css`

## Environment Variables
```
DATABASE_URL=sqlite+aiosqlite:///./portfolio.db  # Dev default
SECRET_KEY=your-secret-key-here
GITHUB_CLIENT_ID=  # Optional OAuth
ENV=development
```

## Services Layer
| Service | Purpose |
|---------|---------|
| `auth.py` | Authentication logic, JWT, OAuth user management |
| `blog.py` | BlogService (CRUD, reactions) + GitHubBlogService (sync posts from GitHub repo) |
| `project.py` | Projects CRUD operations |
| `profile.py` | Profile management with structured data (work, education, skills) |

## Future Considerations
- **Admin Metrics**: Click tracking, page views dashboard
- **Test Coverage**: pytest with async fixtures
- **Repository Layer**: Abstract DB operations from services
- **i18n**: Internationalization support for multi-language content
- **Image Upload**: S3/Cloudflare R2 integration for media

