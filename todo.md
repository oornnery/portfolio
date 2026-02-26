# Refactor TODO (Portfolio)

This document is a full refactor backlog for future iterations.

## Objectives

- Reduce coupling across backend, rendering, and content.
- Make code more Pythonic, typed, and easier to test.
- Improve security defaults and failure behavior.
- Improve observability and diagnostics with full telemetry coverage.
- Evolve Jx components to a clearer feature-oriented composition
  (React/Next-like mindset).
- Keep UX stable while simplifying implementation.

## Current Snapshot

| Area      | Status                                                                                                                       |
| --------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Backend   | Clean baseline with FastAPI + DI + services, but some responsibilities are still mixed.                                      |
| Rendering | Good Jx usage with namespaced catalog folders, but some pages/components are monolithic and repeated patterns remain.        |
| Security  | Good base (CSRF, rate limit, headers), but with important hardening opportunities.                                           |
| Logging   | Structured logs, request correlation, and OpenTelemetry baseline exist; event taxonomy and dashboards still need completion. |
| Frontend  | Visual quality is good, but CSS/JS stack is redundant and partially stale.                                                   |
| Testing   | Lint/type checks pass, but project has no local automated tests yet.                                                         |

## Priority Findings

## P0 (High Impact / Reliability / Security)

- [x] Stop silent template fallback for all errors in `app/dependencies.py`.
  - Current behavior can hide real production bugs and make issues harder to diagnose.
  - Target: fallback only for explicit catastrophic failure paths, and raise in
    debug.

- [x] Remove or gate `static/js/analytics.js` until backend analytics
  endpoints exist.
  - Script sends requests to `/api/v1/analytics/*`, but those routes are not implemented.
  - It also performs invasive fingerprint collection by default.

- [ ] Harden CSP strategy in `app/security.py` + `components/layouts/base.jinja`.
  - Current policy depends on CDN scripts and allows inline styles.
  - Inline JSON-LD script should be nonce/hash-safe or rendered in a
    CSP-compatible way.

- [x] Improve contact delivery guarantees.
  - `ContactNotificationService` logs channel failures but still returns
    success to user.
  - Add explicit policy: either "best-effort with warning" or "fail-fast when
    all channels fail".

- [x] Strengthen CSRF and request validation path.
  - Token is signed and expiring (good) but not bound to user/session context.
  - Add optional token binding (client fingerprint/session secret) and strict
    content-type checks.

- [x] Sanitize markdown HTML before rendering.
  - Markdown from `content/` is trusted today, but safety should be explicit.
  - Add sanitization policy (allowlist) before using `|safe` output.

- [ ] Define a logging contract and map all critical events.
  - Standardize event names, severity, and mandatory attributes.
  - Cover request lifecycle, form pipeline, rendering, and external I/O.

- [x] Add OpenTelemetry tracing and metric instrumentation in backend.
  - Instrument FastAPI, HTTPX, and internal service spans.
  - Emit trace IDs in logs and response headers for correlation.

- [x] Add data protection rules for telemetry.
  - Redact or hash PII in logs, traces, and analytics payloads.
  - Define sampling strategy for traces and high-volume events.

## P1 (Architecture / Decoupling / Maintainability)

- [x] Replace loose frontmatter `dict` usage with typed models.
  - Add `AboutProfile`, `WorkItem`, `EducationItem`, `CertificateItem` schemas.
  - Parse/validate once in `services/markdown.py` and pass typed objects to templates.

- [x] Move profile-global extraction out of `app/dependencies.py`.
  - `dependencies.py` currently reads content and applies profile fallback logic.
  - Create `ProfileService` (application layer) and keep dependencies as pure providers.

- [x] Collapse repeated router render boilerplate.
  - Add helper `render_page(page: PageRenderData) -> HTMLResponse`.
  - Keep routers thin and consistent.

- [x] Split `use_cases.py` into dedicated files.
  - Current file centralizes multiple use-cases and DTOs.
  - Suggested split:
    - `services/use_cases/home.py`
    - `services/use_cases/about.py`
    - `services/use_cases/projects.py`
    - `services/use_cases/contact.py`
    - `services/use_cases/types.py`

- [x] Refactor oversized `components/ui/icon.jinja`.
  - Current file mixes icon glyph rendering and social-links composition with
    many branches.
  - Keep one source of truth for SVGs, but separate concerns:
    - `ui/icon.jinja` (single icon by name)
    - `ui/social_links.jinja` (layout and variants)

- [x] Add Jx Catalog namespaces and prefixed imports.
  - Register optional folders with `catalog.add_folder(..., prefix=...)`.
  - Use prefixed imports like `@ui/...`, `@layouts/...`, and `@cards/...` in components.

- [ ] Decompose large page templates into feature blocks.
  - `pages/home.jinja` and `pages/about.jinja` are doing too much.
  - Break into reusable sections, for example:
    - `features/home/profile_summary.jinja`
    - `features/home/projects_preview.jinja`
    - `features/home/contact_preview.jinja`
    - `features/resume/header.jinja`
    - `features/resume/experience_list.jinja`

- [ ] Introduce strict context contracts for page templates.
  - Avoid passing raw mixed dictionaries.
  - Use explicit structures so each page gets only what it needs.

- [x] Build an analytics domain with typed events and ingestion service.
  - Create event schemas for page views, clicks, outbound links, and form usage.
  - Validate events server-side before exporting to telemetry backend.

- [x] Replace ad-hoc frontend tracking with explicit event API.
  - Keep client script minimal and declarative (`data-analytics-*`).
  - Emit only events backed by implemented backend endpoints.

## P2 (Frontend Stack Simplification)

- [x] Consolidate CSS strategy.
  - Current runtime includes `tokens.css`, `motion.css`, `style.css`;
    `global.css` exists but is unused.
  - Choose one canonical style entry point and remove dead styles.

- [ ] Remove Tailwind CDN runtime dependency in production.
  - Prefer build-time CSS (compiled Tailwind or pure CSS tokens/utilities).
  - Improves performance, security, and CSP strictness.

- [ ] Remove dead JS code paths.
  - `static/js/main.js` still includes share/copy helper flows no longer used
    by current templates.
  - Keep only behavior that has active DOM hooks.

- [x] Remove unused artifacts and keep runtime minimal.
  - Review `static/js/htmx.js` vs `htmx.min.js`.
  - Review unused components like `components/hero/hero.jinja`.

## Observability and Analytics Roadmap (OTel)

- [x] Create telemetry bootstrap module (`app/telemetry.py`).
  - Initialize OTel `TracerProvider`, `MeterProvider`, and log correlation.
  - Configure exporters (OTLP by default; console in local debug).

- [x] Instrument HTTP layer with standard semantic conventions.
  - Server spans: route, status code, latency, exception class.
  - Client spans for webhook/email provider calls.

- [x] Add application metrics for portfolio behavior.
  - Counters: page views by route, contact submissions, submission failures.
  - Histograms: request latency, render latency, notification latency.
  - Gauges/up-down counters: in-flight requests and active limiter hits.

- [x] Add frontend interaction analytics with privacy-safe defaults.
  - Track page_view, click, outbound_click, section_scroll, and contact_attempt.
  - Avoid fingerprinting by default; keep opt-in and configurable.

- [ ] Add dashboards and alerts (SLO-oriented).
  - Error rate, p95 latency, contact success ratio, webhook/email failure rate.
  - Alert on abnormal spike of 4xx/5xx or notification channel degradation.
  - This should be configured and exported through OpenTelemetry and consumed
    by observability tools like Grafana and Datadog.

## P3 (Quality / Testability / DX)

- [ ] Add baseline tests (missing today).
  - Unit tests for:
    - `validate_csrf_token`
    - frontmatter parsing and typed validation
    - contact submission validation and error mapping
    - SEO URL composition
  - Integration tests for:
    - `GET /`, `/about`, `/projects`, `/projects/{slug}`, `/contact`
    - `POST /contact` success/failure paths

- [ ] Add snapshot-like rendering tests for critical pages.
  - Validate key sections exist and avoid accidental UI regressions.

- [x] Add CI pipeline for `ruff`, `ty`, tests, and markdown lint.

- [ ] Add architecture decision records (ADR-lite).
  - Document why chosen for CSP policy, analytics policy, content schema, and
    component boundaries.

## Proposed Target Structure (Incremental)

```text
app/
  core/
    config.py
    logger.py
    security.py
  domain/
    models.py
    schemas.py
  application/
    use_cases/
      home.py
      about.py
      projects.py
      contact.py
      types.py
    services/
      profile.py
      seo.py
  observability/
    telemetry.py
    logging.py
    analytics.py
    events.py
  infrastructure/
    markdown.py
    notifications/
      contact.py
  presentation/
    dependencies.py
    routers/
      home.py
      about.py
      projects.py
      contact.py
    render.py
  main.py

components/
  layouts/
    base.jinja
    home.jinja
    public.jinja
  pages/
    home.jinja
    about.jinja
    projects.jinja
    project_detail.jinja
    contact.jinja
    not_found.jinja
    maintenance.jinja
  ui/
    button.jinja
    input.jinja
    alert.jinja
    breadcrumb.jinja
    card.jinja
    tag.jinja
    icon.jinja
    social_links.jinja
    section_link.jinja
  features/
    home/
    resume/
    projects/
    contact/
```

## Execution Plan (Suggested)

| Phase   | Focus                            | Expected Outcome                                         |
| ------- | -------------------------------- | -------------------------------------------------------- |
| Phase 1 | Reliability + security hardening | Safer defaults and clearer failure behavior              |
| Phase 2 | Observability and telemetry      | End-to-end logs/traces/metrics with correlated IDs       |
| Phase 3 | Backend separation               | Cleaner DI graph, typed content pipeline, thinner routers|
| Phase 4 | Component decomposition          | Smaller reusable building blocks, less template coupling |
| Phase 5 | CSS/JS cleanup                   | Smaller runtime, fewer duplicate layers                  |
| Phase 6 | Testing + CI                     | Safer refactors and faster iteration                     |

## Quick Wins (Can Start Immediately)

- [x] Remove unused `global.css` from repository or wire it intentionally.
- [x] Remove dead functions in `static/js/main.js` not used by templates.
- [x] Add `debug` behavior to `render_template` to re-raise template errors.
- [x] Add typed `About` schema and remove ad-hoc `meta.get(...)` chains.
- [x] Create `ui/social_links.jinja` and simplify `ui/icon.jinja`.
- [x] Add first test module for contact submission flow.
- [x] Add trace/log correlation (`trace_id`, `span_id`, `request_id`) in log output.
- [x] Create initial analytics event schema and instrument `page_view` + `click`.

## Recent Progress (2026-02-26)

- [x] Standardize home section start alignment so home/projects/contact start
  on the same visual line.
- [x] Anchor home contact footer inside the contact section and remove
  oversized footer gap.
- [x] Reduce footer visual height to match the about page density and spacing.
- [x] Fine-tune home contact vertical offset (moved slightly lower for better
  balance with navbar and footer).

## Definition of Done for Refactor

- [ ] No dead runtime assets.
- [x] No broad fallback masking template failures in debug.
- [ ] Content parsing is typed and validated.
- [ ] Page templates are composed from smaller feature components.
- [ ] Contact flow has explicit delivery policy and tests.
- [ ] CSP is strict and compatible with actual assets.
- [x] CI checks lint + types + tests on every change.
- [ ] OTel traces, metrics, and logs are correlated and queryable.
- [ ] Analytics events are typed, privacy-safe, and backed by dashboards.
