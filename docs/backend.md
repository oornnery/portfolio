# Backend

## Layered Structure

| Layer          | Path                   | Responsibility                                       |
| -------------- | ---------------------- | ---------------------------------------------------- |
| Entry point    | `app/main.py`          | App factory, middleware, startup wiring              |
| Routing        | `app/api/*`            | HTTP endpoints and dependency injection              |
| Use-cases      | `app/services/*`       | Page building and business orchestration             |
| Domain         | `app/domain/*`         | Typed schemas and entities                           |
| Infrastructure | `app/infrastructure/*` | Markdown IO, sanitization, notifications             |
| Rendering      | `app/rendering/*`      | Typed page render path                               |
| Core           | `app/core/*`           | Settings, security, logging, dependencies, utilities |
| Observability  | `app/observability/*`  | Analytics service and app metrics                    |

## App Factory

`create_app()` in `app/main.py` configures:

- Structured logging (`configure_logging`)
- FastAPI docs toggled by `DEBUG`
- Static mount at `/static`
- Telemetry (`configure_telemetry`)
- Middlewares (security headers, body limits, analytics guard, tracing, CORS,
  host validation)
  - All custom middleware uses pure ASGI protocol
- Rate-limit exception handler
- Router inclusion via `app/api/router.py`
- Rendered 404 page handler

## API Endpoints

### Page routes

- `GET /` -> `HomePageService.build_page()`
- `GET /about` -> `AboutPageService.build_page()`
- `GET /projects` -> `ProjectsPageService.build_list_page()`
- `GET /projects/{slug}` -> detail page or HTTP 404
- `GET /contact` -> `ContactPageService.build_page()`

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
- Emits analytics events for attempt/failure/success
- Returns `ContactFormResult` with page, status code, and outcome

### Analytics route

- `POST /api/v1/analytics/track`
- Input: `AnalyticsTrackRequest` (`events` max 50)
- Output: `AnalyticsTrackResponse` with accepted/rejected counts
- Protected by source validation and route-specific rate limit

## Service Responsibilities

| Service                    | Responsibility                                  |
| -------------------------- | ----------------------------------------------- |
| `HomePageService`          | Featured projects + home SEO + CSRF token       |
| `AboutPageService`         | About markdown/frontmatter to page context      |
| `ProjectsPageService`      | Projects listing and detail context             |
| `ContactPageService`       | Contact page state and feedback messages        |
| `ContactSubmissionService` | CSRF + schema validation and status mapping     |
| `ContactOrchestrator`      | Full contact flow: validation, notify, metrics  |
| `ProfileService`           | Global profile data from `content/about.md`     |

## Domain Contracts

Defined in `app/domain/schemas.py`:

- `ContactForm`: strict form schema (`extra="forbid"`)
- `AboutFrontmatter` and content models
- `ProjectFrontmatter` and normalized metadata
- Analytics schemas (`AnalyticsTrackEvent`, request/response)

Typed page contexts in `app/services/types.py` ensure stable template contracts.

## Content Pipeline

`app/infrastructure/markdown.py`:

1. Parse YAML frontmatter
2. Convert markdown to HTML
3. Sanitize HTML with nh3 (Rust-based ammonia bindings) using strict allowlists
4. Cache content with TTLCache (`MARKDOWN_CACHE_TTL`, default 300s, 0 = indefinite)

Thread-safe caching with `threading.Lock` for safety under multi-worker Uvicorn.
This keeps content authoring simple while reducing XSS risk.

## Notifications

`ContactNotificationService` dispatches channel sends in parallel:

- `WebhookNotificationChannel` (HTTPX)
- `EmailNotificationChannel` (SMTP/SMTP_SSL)

Per-channel metrics capture outcome and latency.

## Observability in Backend

- Request lifecycle metrics in `app/observability/metrics.py`
- Structured event logs with request/trace IDs
- Analytics counter metrics in `app/observability/analytics.py`
- Trace, metrics, and logs exporter setup in `app/observability/telemetry.py`
