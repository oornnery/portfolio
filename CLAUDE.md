# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run dev server
uv run task run                    # uvicorn with --reload on port 8000

# Lint & format
uv run task fmt                    # ruff format + rumdl fmt
uv run task lint                   # ruff check app tests app/static/js
uv run task typecheck              # ty check app

# Tests
uv run task test                   # pytest -q (all tests)
uv run pytest tests/test_foo.py -q # single test file
uv run pytest -k "test_name" -q   # single test by name
uv run task test_routes            # route tests with 100% coverage gate
uv run task test_security          # security-focused tests

# Full CI check
uv run task ci                     # fmt + lint + typecheck + test + md_check + jx_check

# Jx template validation
DEBUG=true PYTHONPATH=. uv run jx check app/catalog.py:catalog
```

Pre-commit hooks run ruff format, ruff check --fix, ty check, and rumdl fmt/check.

## Architecture

SSR portfolio app: FastAPI backend renders HTML via Jx/Jinja templates. No SPA framework.

### Layer map

| Layer          | Path                       | Role                                         |
| -------------- | -------------------------- | -------------------------------------------- |
| Entry point    | `app/main.py`              | App factory (`create_app`), middleware stack |
| Routing        | `app/api/*`                | Thin routers that delegate to services       |
| Services       | `app/services/*`           | Page builders and orchestrators              |
| Models         | `app/models/*`             | Pydantic schemas and models                  |
| Infrastructure | `app/infrastructure/*`     | Markdown IO, sanitization, notifications     |
| Rendering      | `app/core/dependencies.py` | Jx Catalog setup and `render_template`       |
| Core           | `app/core/*`               | Settings, security middleware, logging       |
| Observability  | `app/observability/*`      | OpenTelemetry, analytics service             |
| Templates      | `app/templates/`           | `ui/` (subfolders), `layouts/`, `features/`, `pages/` |
| Content        | `content/`                 | Markdown files (about, projects, blog)       |

### Key patterns

- **Routers are thin**: they call a service method and return `HTMLResponse`. Business logic lives in services.
- **Orchestrator pattern**: complex flows like contact submission use `ContactOrchestrator` which composes validation, notification, and analytics services.
- **Content pipeline**: markdown files in `content/` are parsed (YAML frontmatter + body), converted to HTML, sanitized with nh3, and cached with TTLCache. `content/about.md` uses markdown `##`/`###` headings to define resume sections.
- **Jx Catalog**: components are registered with prefixes (`@ui/`, `@layouts/`, `@features/`, `@pages/`) in `app/core/dependencies.py`. Templates declare args with `{# def ... #}` and compose via `{% call %}`.
- **Page context contracts**: typed dataclasses in `app/services/types.py` define what each page template receives.
- **Pure ASGI middleware**: all custom middleware (security headers, body limits, tracing, analytics guard) uses raw ASGI protocol, not `BaseHTTPMiddleware`.
- **Settings**: `app/core/config.py` uses `pydantic-settings` reading from `.env`. Copy `.env.example` to `.env` before running.

### Styling

Tailwind CSS (generated via `tailwind.config.cjs`) plus custom CSS layers: `tokens.css` (semantic tokens), `motion.css` (animations), `style.css` (app-specific). Vanilla JS for progressive enhancement.

Color tokens use RGB channels (`--accent-rgb`, `--warn-rgb`, `--danger-rgb`, `--accent-2-rgb`) so Tailwind opacity modifiers work: `bg-accent/10`, `border-accent/20`. Active theme and palette are set on `<html>` via `data-theme` (dark/light) and `data-palette` (default/ocean/sunset/rose/forest/mono). Palette overrides live in `tokens.css` as `:root[data-palette="..."]` blocks that come after the `data-theme` block in the cascade — cascade order matters.

### UI component paths

`ui/` is split into subfolders registered recursively under the `@ui/` prefix:

| Subfolder    | Components                                                                                              |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| `ui/layout/` | `center`, `grid`, `row`, `section`, `stack`                                                             |
| `ui/nav/`    | `breadcrumb`, `footer`, `navbar`, `scroll-indicator`                                                    |
| `ui/card/`   | `card`, `card-heading`                                                                                  |
| `ui/form/`   | `button`, `input`                                                                                       |
| `ui/` root   | `alert`, `avatar`, `content-shell`, `empty-state`, `icon`, `meta-info`, `page-header`, `section-link`, `seo-head`, `social-links`, `tag` |

Import with the full subfolder path: `{#import "@ui/form/button.jinja" as Button #}`
