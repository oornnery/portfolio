---
trigger: always_on
---

# Portfolio Project Guidelines

FastAPI + **Jx** (JinjaX) + HTMX portfolio with blog, projects, analytics, and admin panel.

> **Jx Reference**: https://github.com/jpsca/jx  
> **HTMX Reference**: https://htmx.org

---

## Architecture

```
app/
├── main.py             # FastAPI app, middlewares, routers, lifespan
├── config.py           # Pydantic-settings (loads from .env)
├── catalog.py          # Jx Catalog singleton
├── db.py               # Async SQLModel engine
├── views/              # HTML routes (public + admin)
├── api/v1/             # JSON API endpoints
├── components/         # Jx components (.jinja files)
│   ├── layouts/        # Base, Admin, Home layouts
│   ├── ui/             # Button, Card, Input, Tag, Icon, etc.
│   ├── pages/          # Full page components
│   ├── blog/           # Blog-specific partials
│   └── admin/          # Admin panel components
├── models/             # SQLModel schemas
├── services/           # Business logic packages (e.g., blog/)
├── core/               # Auth, deps, telemetry
├── middleware/         # Security, logging, analytics
└── static/             # CSS (tokens.css, motion.css), JS, htmx.js
logs/                   # Telemetry and application logs
```

---

## Jx (JinjaX) Components

Components live in `app/components/` and are used like HTML tags.

### Defining Components

All component files MUST use **CamelCase.jinja** naming.

```jinja
{# app/components/ui/Button.jinja #}
{#def variant="default", size="default", href="", disabled=False #}

<button class="{{ variant_classes[variant] }}" {{ attrs.render() }}>
    {{ content }}
</button>
```

### Using Components

```jinja
<Button variant="primary" size="lg">Click me</Button>
<Card title="My Card">Card content here</Card>
<Input name="email" type="email" placeholder="Email" />
```

### Catalog Setup (`app/catalog.py`)

```python
from jx import Catalog
catalog = Catalog(folder=Path("app/components"), auto_reload=settings.is_development)
catalog.jinja_env.globals["settings"] = settings
```

---

## HTMX Patterns

### Partial Response Pattern

Check `HX-Request` header to return partials for HTMX, full pages otherwise. For POST endpoints that update a list, **return the HTML fragment** instead of JSON.

```python
@router.post("/comments", response_class=HTMLResponse)
async def create_comment(request: Request, ...):
    # logic...
    if request.headers.get("HX-Request"):
        return catalog.render("blog/Comments.jinja", comments=all_comments)
    return comment_json
```

---

## Encoding & Special Characters

To prevent corrupted characters (e.g., `â˜…` instead of `★`) across different environments:
- Use **HTML Entities** for non-ASCII characters in `.jinja` files.
- `★` &rarr; `&#9733;`
- `•` &rarr; `&bull;`
- `ã` &rarr; `&#227;`
- `✕` &rarr; `&times;`

---

## Security

### Middleware Stack (`app/main.py`)

Middlewares execute in reverse order (last added = first to execute):

```python
app.add_middleware(SlowAPIMiddleware)         # Rate limiting
app.add_middleware(RequestLoggingMiddleware)   # Request logs
app.add_middleware(AnalyticsMiddleware)        # Visitor tracking
app.add_middleware(SecurityMiddleware)         # OWASP headers + HTMX validation
app.add_middleware(TrustedHostMiddleware)      # Host header injection (prod)
app.add_middleware(CORSMiddleware)             # CORS
```

---

## Telemetry & Logging

- Spans must be exported to `logs/telemetry.log` to keep the terminal clean.
- Use `FileSpanExporter` for persistent tracing.
- Never commit the `logs/` directory.

---

## Development Commands

```bash
# Install & run
uv sync
uv run uvicorn app.main:app --reload

# Quality checks (REQUIRED before commits)
uv run ruff format . && uv run ruff check . --fix --unsafe-fixes
uv run ty check .
uv run pytest -v
```

---

## Python Coding Standards

- Use `pathlib` instead of `os.path`
- Use `f-strings` only
- Prefer early returns
- Use `logging`, not `print`
- Modern typing: `str | None`, `list[str]`
- **Services**: Split complex services into packages (e.g., `app/services/blog/`) with an `__init__.py`.

---

## Naming Conventions

| Type | Location | Pattern |
|------|----------|---------|
| Views | `app/views/public/` or `admin/` | `{entity}.py` |
| Components | `app/components/{category}/` | `CamelCase.jinja` |
| Models | `app/models/` | `{entity}.py` |
| Services | `app/services/{package}/` | `{entity}_service.py` |

---

## Agent Safety Protocol

- Always read files before editing.
- Never delete files without confirmation.
- Always run formatter & linter after edits.
- Use HTML entities for icons/special chars in templates.
