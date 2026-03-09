# Backend

## Layered Structure

| Layer          | Path                    | Responsibility                                       |
| -------------- | ----------------------- | ---------------------------------------------------- |
| Entry point    | `app/main.py`           | App factory, middleware, startup wiring              |
| Routing        | `app/api/*`             | HTTP endpoints and dependency injection              |
| Use-cases      | `app/services/*`        | Page building and business orchestration             |
| Domain         | `app/models/*`          | Typed schemas and entities                           |
| Infrastructure | `app/infrastructure/*`  | Markdown IO, sanitization, notifications             |
| Rendering      | `app/core/rendering.py` | `render_page`, `render_fragment`, `is_htmx` helpers  |
| Core           | `app/core/*`            | Settings, security, logging, dependencies, utilities |
| Observability  | `app/observability/*`   | OpenTelemetry bootstrap and app metrics              |

## App Factory

`create_app()` in `app/main.py` configures:

- Structured logging (`configure_logging`)
- FastAPI docs toggled by `DEBUG`
- Static mount at `/static`
- Telemetry (`configure_telemetry`)
- Middlewares (security headers, body limits, tracing, CORS,
  host validation)
  - All custom middleware uses pure ASGI protocol
- Rate-limit exception handler
- Router inclusion via `app/api/router.py`
- Rendered 404 page handler

## API Endpoints

### Page routes

- `GET /` -> `HomePageService.build_page()`
- `GET /about` -> `AboutPageService.build_page()`
- `GET /projects?page=N` -> `ProjectsPageService.build_list_page()`
  (paginated, htmx fragment support)
- `GET /projects/{slug}` -> detail page or HTTP 404
- `GET /blog` -> `BlogPageService.build_home_page()`
- `GET /blog/posts?page=N` -> `BlogPageService.build_posts_page()` (paginated)
- `GET /blog/posts/{slug}` -> blog post detail or HTTP 404
- `GET /blog/tags` -> tags overview page (htmx fragment support)
- `GET /blog/tags/{tag}` -> posts filtered by tag (htmx fragment support)
- `GET /blog/feed.xml` -> RSS feed (`application/rss+xml`)
- `GET /contact` -> `ContactPageService.build_page()`
- `POST /otel/v1/traces` -> same-origin OTLP HTTP proxy for browser traces

### Health check

- `GET /health` returns `{"status": "ok"}`
- Exempt from rate limiting
- Skipped by request tracing middleware
- Used by Docker healthcheck probes

### Form route

- `POST /contact`
- Thin router delegates to `ContactOrchestrator.handle_submission()`
- Orchestrator validates content type, CSRF, and Pydantic constraints
- Dispatches webhook/SMTP channels concurrently
- Emits span events for attempt/failure/success on the current request trace
- Returns `ContactFormResult` with page, status code, and outcome
- On htmx request (`HX-Request` header), returns only the form fragment
  instead of a full page — enables inline validation error display

## Service Responsibilities

| Service                    | Responsibility                                  |
| -------------------------- | ----------------------------------------------- |
| `HomePageService`          | Featured projects + home SEO + CSRF token       |
| `AboutPageService`         | About markdown/frontmatter to page context      |
| `ProjectsPageService`      | Projects listing and detail context             |
| `BlogPageService`          | Blog home, posts, tags, detail, and RSS feed    |
| `ContactPageService`       | Contact page state and feedback messages        |
| `ContactSubmissionService` | CSRF + schema validation and status mapping     |
| `ContactOrchestrator`      | Full contact flow: validation, notify, metrics  |
| `ProfileService`           | Global profile data from `content/about.md`     |

## Domain Contracts

Defined in `app/models/schemas.py`:

- `ContactForm`: strict form schema (`extra="forbid"`)
- `AboutFrontmatter` and content models
- `ProjectFrontmatter` and normalized metadata
- `BlogPostFrontmatter` and normalized blog metadata
  - Supports optional `gist_url` and `gist_file`

Typed page contexts in `app/services/types.py` ensure stable template contracts.

## Rendering Helpers

`app/core/rendering.py` provides three helpers:

- `render_page(page: PageRenderData)` — renders a full page template
- `render_fragment(template, **context)` — renders a component template
  directly (used for htmx fragment responses)
- `is_htmx(request)` — detects `HX-Request: true` header

Routes that support htmx check `is_htmx()` and return a fragment instead of a
full page. This enables progressive enhancement: the same route serves both
full-page loads and in-page fragment swaps.

## Pagination

Blog posts (`/blog/posts`) and projects (`/projects`) support SSR pagination
via `?page=N` query parameter. Services accept `page` and `page_size`
(default 10), clamp to `[1, total_pages]`, and include `page` and
`total_pages` in the page context for the `@ui/nav/pagination.jinja` component.

## Content Pipeline

`app/infrastructure/markdown.py`:

1. Parse YAML frontmatter
2. For `content/about.md`, parse authored body sections from markdown headings
   (`##` section, `###` entry) into typed resume content
3. Convert markdown to HTML
4. Sanitize HTML with nh3 (Rust-based ammonia bindings) using strict allowlists
5. Cache content with TTLCache (`MARKDOWN_CACHE_TTL`, default 300s, 0 = indefinite)

Thread-safe caching with `threading.Lock` for safety under multi-worker Uvicorn.
This keeps content authoring simple while reducing XSS risk.
The pipeline currently ingests `content/about.md`, `content/projects/*.md`,
and `content/blog/*.md`.
`content/about.md` now keeps only profile metadata in frontmatter; the resume
body is authored in markdown sections and parsed into structured page content.
For blog posts, if body markdown is empty and `gist_url` is provided,
the loader fetches gist markdown content from GitHub API/raw endpoints.
When `gist_url` is provided, gist comments are also fetched and rendered
in the post detail page.

## Notifications

`ContactNotificationService` dispatches channel sends in parallel:

- `WebhookNotificationChannel` (HTTPX)
- `EmailNotificationChannel` (SMTP/SMTP_SSL)

Per-channel metrics capture outcome and latency.

## Observability in Backend

- Request lifecycle metrics in `app/observability/metrics.py`
- Structured event logs with request/trace IDs
- Trace, metrics, and logs exporter setup in `app/observability/telemetry.py`
- Helper functions in `app/observability/telemetry.py` attach manual span
  attributes/events to the current request
- `app/api/telemetry.py` forwards browser OTLP HTTP payloads to the collector
  derived from `TELEMETRY_EXPORTER_OTLP_ENDPOINT` (or overridden by
  `FRONTEND_TELEMETRY_OTLP_ENDPOINT`)
- `configure_telemetry()` auto-detects preconfigured global providers
  (for `opentelemetry-instrument`) and reuses them instead of trying to
  override tracer/meter/logger providers a second time
- `usercustomize.py` maps `.env` telemetry settings to `OTEL_*` variables
  early enough for direct `opentelemetry-instrument` runs, so shell launches
  and app-managed launches share the same collector and `service.name`
- FastAPI and HTTPX instrumentation are only applied when they are not already
  instrumented
