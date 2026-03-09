# CLAUDE.md

Operational guide for Claude Code and other coding agents working in this
repository.

## Commands

```bash
# Install dependencies
uv sync && npm install

# Build assets (JS bundle + Tailwind CSS)
uv run task build                  # build_js + build_css
uv run task build_js               # esbuild IIFE bundle → app/static/js/main.js
uv run task build_css              # tailwindcss → app/static/css/tailwind.css
uv run task watch_js               # esbuild watch mode for development

# Run dev server
uv run task run                    # uvicorn with --reload on port 8000
uv run task run_otel               # opentelemetry-instrument + uvicorn (requires exported OTEL_*)

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

SSR personal site: FastAPI backend renders HTML via Jx/Jinja templates. No SPA
framework. Progressive enhancement via Alpine.js (reactive state), Stimulus
(controllers), and htmx (fragment swaps).

### Layer map

| Layer          | Path                       | Role                                                  |
| -------------- | -------------------------- | ----------------------------------------------------- |
| Entry point    | `app/main.py`              | App factory (`create_app`), middleware stack          |
| Routing        | `app/api/*`                | Thin routers that delegate to services                |
| Services       | `app/services/*`           | Page builders and orchestrators                       |
| Models         | `app/models/*`             | Pydantic schemas and models                           |
| Infrastructure | `app/infrastructure/*`     | Markdown IO, sanitization, notifications              |
| Rendering      | `app/core/dependencies.py` | Jx Catalog setup and `render_template`                |
| Rendering      | `app/core/rendering.py`    | `render_page`, `render_fragment`, `is_htmx`           |
| Core           | `app/core/*`               | Settings, security middleware, logging                |
| Observability  | `app/observability/*`      | OpenTelemetry bootstrap and app metrics               |
| Templates      | `app/templates/`           | `ui/` (subfolders), `layouts/`, `features/`, `pages/` |
| Content        | `content/`                 | Markdown files (about, projects, blog)                |

### Key patterns

- **Routers are thin**: they call a service method and return `HTMLResponse`.
  Business logic lives in services. Routes that support htmx use `is_htmx()`
  to detect `HX-Request` header and return a fragment via `render_fragment()`
  instead of a full page.
- **Orchestrator pattern**: complex flows like contact submission use
  `ContactOrchestrator` which composes validation, notification, and telemetry
  span events.
- **Content pipeline**: markdown files in `content/` are parsed (YAML
  frontmatter + body), converted to HTML, sanitized with nh3, and cached with
  TTLCache. `content/about.md` uses markdown `##`/`###` headings to define
  resume sections.
- **Jx Catalog**: components are registered with prefixes (`@ui/`,
  `@layouts/`, `@features/`, `@pages/`) in `app/core/dependencies.py`.
  Templates declare args with `{# def ... #}` and compose via `{% call %}`.
- **Page context contracts**: typed dataclasses in `app/services/types.py`
  define what each page template receives.
- **Pure ASGI middleware**: all custom middleware (security headers, body
  limits, tracing) uses raw ASGI protocol, not
  `BaseHTTPMiddleware`.
- **Settings**: `app/core/config.py` uses `pydantic-settings` reading from
  `.env`. Copy `.env.example` to `.env` before running.
- **Shared utilities**: place reusable helpers in `app/core/utils.py` to
  avoid duplication across services.

### Styling

Tailwind CSS (generated via `tailwind.config.cjs`) plus custom CSS layers:
`tokens.css` (semantic tokens), `motion.css` (animations), `style.css`
(app-specific).

### Frontend JS stack

JS source lives in `app/static/js/src/` and is bundled by esbuild into a
single IIFE at `app/static/js/main.js`.

| Framework   | Role                          | Components                                |
| ----------- | ----------------------------- | ----------------------------------------- |
| Alpine.js   | Reactive state and toggles    | `navbar`, `palette`, `carousel`, `contactForm` |
| Stimulus    | Lifecycle-bound controllers   | `toc-controller`, `reading-progress`      |
| htmx        | Fragment swaps and SSR forms  | Contact form, blog tags, projects filter  |
| OTel JS     | Browser tracing + manual spans| `telemetry`, contact/form events          |

Color tokens use RGB channels (`--accent-rgb`, `--warn-rgb`, `--danger-rgb`,
`--accent-2-rgb`) so Tailwind opacity modifiers work: `bg-accent/10`,
`border-accent/20`. Active theme and palette are set on `<html>` via
`data-theme` (dark/light) and `data-palette`
(default/ocean/sunset/rose/forest/mono). Palette overrides live in
`tokens.css` as `:root[data-palette="..."]` blocks that come after the
`data-theme` block in the cascade — cascade order matters.

### UI component paths

`ui/` is split into subfolders registered recursively under the `@ui/`
prefix:

| Subfolder    | Components                                                   |
| ------------ | ------------------------------------------------------------ |
| `ui/layout/` | `center`, `grid`, `row`, `section`, `stack`                  |
| `ui/nav/`    | `breadcrumb`, `footer`, `navbar`, `pagination`, `scroll`,    |
|              | `section`, `social`                                          |
| `ui/card/`   | `card`, `card/heading`                                       |
| `ui/content/`| `header`, `meta`, `shell`                                    |
| `ui/feedback/` | `alert`, `empty`                                           |
| `ui/form/`   | `button`, `input`                                            |
| `ui/` root   | `avatar`, `icon`, `seo`, `tag`                               |

Import with the full subfolder path:
`{#import "@ui/form/button.jinja" as Button #}`

## Architecture Rules (Mandatory)

1. Keep routers thin — HTTP input/output only.
2. Put business logic in services; use orchestrator classes for multi-step
   flows (e.g. `ContactOrchestrator`).
3. Keep templates typed through context models in `app/services/types.py`.
4. Render pages via `render_page()` and `PageRenderData`. For htmx
   fragment responses, use `render_fragment()` with `is_htmx()` detection.
5. Do not bypass the content pipeline in `app/infrastructure/markdown.py`.
6. Reuse existing dependencies from `app/core/dependencies.py`.
7. Write new middleware as pure ASGI (`__init__(self, app: ASGIApp)` +
   `async __call__(self, scope, receive, send)`). Never use
   `BaseHTTPMiddleware`.

## Security Baseline (Do Not Regress)

Application-level controls — never remove or weaken without explicit approval:

- CSRF generation + validation for form submission
- Allowed form content-type validation
- Body size limits (global + route-specific)
- Default rate limit for all routes (proxy-aware via `extract_source_ip`)
- Route-specific limits for sensitive endpoints
- Security headers middleware (CSP strict in prod, relaxed in dev)
- Trusted host middleware
- CORS policy from settings
- HTML sanitization via nh3 with strict tag/attribute allowlists

## Test Requirements

Before finishing any change, run:

```bash
uv run task ci
```

When adding or changing behavior:

1. Add or update route/integration tests.
2. Add or update security tests for hostile inputs and abuse scenarios.
3. Keep API route coverage at 100% (`uv run task test_routes`).

Security scenarios expected in coverage: CSRF misuse, input validation bypass,
size/flood abuse, host/CORS misconfiguration, traversal/injection payloads.

## Documentation Policy

When architecture, security, infra, or design changes — update docs in the
same commit:

- `docs/architecture.md`, `docs/backend.md`, `docs/frontend.md`
- `docs/infrastructure.md`, `docs/security.md`
- `docs/design-system.md`, `docs/figma-tokens.md`
- `README.md` (keep concise, link to docs)

## Commit Guidelines

Prefer small commits by concern/type:

- `feat:` — new behavior
- `fix:` — bug fixes
- `refactor:` — structural changes with no behavior change
- `test:` — test-only changes
- `docs:` — documentation only
- `chore:` / `build:` — tooling, config, dependencies

Do not bundle unrelated refactors into feature or security fixes.
Include test updates with behavior changes.

## Agent Checklist

Before starting:

1. Read `README.md` and `docs/README.md`.
2. Confirm target files and impact scope.

Before finishing:

1. Run `uv run task ci` (fmt + lint + typecheck + test + md_check + jx_check).
2. Validate route/security behavior for changed endpoints.
3. Update docs if behavior or contracts changed.
4. Commit in small logical units by type.
