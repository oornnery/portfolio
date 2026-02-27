# AGENTS.md

Operational instructions for engineers and coding agents working in this
repository.

## 1. Mission

Build and maintain a production-ready portfolio web app using:

- FastAPI for HTTP and middleware
- Jx + Jinja for server-side rendering
- Markdown frontmatter as content source
- Docker + Traefik for deployment
- OpenTelemetry for observability

Primary goals:

- Keep architecture clean and predictable
- Keep security controls enabled by default
- Keep test and CI quality gates green

## 2. Project Map

- `app/main.py`: FastAPI app factory and middleware wiring
- `app/api/*`: thin routers (HTTP input/output only)
- `app/services/*`: use-case orchestration (includes `ContactOrchestrator`)
- `app/domain/*`: schemas and domain models
- `app/core/utils.py`: shared utilities (`split_csv`, etc.)
- `app/infrastructure/*`: markdown IO/sanitization (nh3) and notification channels
- `app/rendering/*`: typed render path (`PageRenderData` -> HTML)
- `app/components/*`: Jx/Jinja components
- `app/static/*`: CSS/JS/assets
- `content/*`: markdown source for profile and projects
- `docker/*`: Dockerfiles, compose files, Traefik config
- `infra/*`: observability assets and runbooks
- `tests/*`: route, integration, markdown, and security tests
- `docs/*`: full architecture and implementation documentation

## 3. Architecture Rules (Mandatory)

1. Keep routers thin.
2. Put business logic in services; use orchestrator classes for multi-step flows
   (e.g. `ContactOrchestrator`).
3. Keep templates typed through context models in `app/services/types.py`.
4. Render pages via `render_page()` and `PageRenderData`.
5. Do not bypass the content pipeline in `app/infrastructure/markdown.py`.
6. Reuse existing dependencies from `app/core/dependencies.py` (cached
   singletons where appropriate).
7. Write new middleware as pure ASGI (`__init__(self, app: ASGIApp)` +
   `async __call__(self, scope, receive, send)`). Do not use `BaseHTTPMiddleware`.
8. Place shared utilities in `app/core/utils.py` to avoid duplication.

## 4. Jx and Template Conventions

Use Jx prefixes registered in `get_catalog()`:

- `@ui/*`
- `@layouts/*`
- `@features/*`
- `@pages/*`

Do:

- Reuse existing UI components (`button`, `input`, `card`, etc.).
- Prefer composition over one-off page markup.
- Keep template contracts explicit (`{#def ... #}` only for required props).

Do not:

- Import templates using ad-hoc absolute paths.
- Duplicate existing UI behavior already implemented in shared components.

## 5. Security Baseline (Do Not Regress)

Application-level controls are required:

- CSRF generation + validation for form submission
- Allowed form content-type validation
- Body size limits (global + route-specific)
- Default rate limit for all routes (proxy-aware via `extract_source_ip`)
- Route-specific limits for sensitive endpoints
- Security headers middleware (CSP strict in prod, relaxed in dev)
- Trusted host middleware
- CORS policy from settings
- Analytics source allowlist checks
- HTML sanitization via nh3 with strict tag/attribute allowlists

Edge-level controls (Traefik in production) are required:

- Rate limiting
- In-flight request cap
- Request body limits
- Analytics IP allowlist

Never:

- Remove or weaken security middleware without explicit approval
- Log raw secrets, tokens, or sensitive user content

## 6. Observability Rules

- Keep OpenTelemetry instrumentation enabled by config.
- Preserve request IDs and trace correlation in logs.
- When adding endpoints, ensure they produce meaningful telemetry.
- Keep metric names and event naming consistent with existing conventions.

Related docs:

- `infra/README.md`
- `docs/security.md`
- `docs/infrastructure.md`

## 7. Coding Standards

Python:

- Python 3.12+
- Type hints for public function signatures
- Pydantic models for external input/output contracts
- Prefer explicit errors and stable status-code mapping

Frontend:

- Keep SSR-first approach
- Keep JS lightweight and progressive
- Keep design tokens consistent with `tokens.css` and documented mappings

Formatting and lint:

- `ruff format .`
- `ruff check app tests app/static/js`
- `ty check app`
- `rumdl check .`

## 8. Test Requirements

Before merge, run:

- `pytest -q`
- API route coverage gate:
  - `pytest --cov=app/api --cov-report=term-missing --cov-fail-under=100 -q`

When adding/changing behavior:

1. Add or update route/integration tests.
2. Add or update security tests for hostile inputs and abuse scenarios.
3. Validate markdown and sanitization behavior when content pipeline changes.
4. Keep existing OWASP-oriented tests passing.

Security scenarios expected in coverage:

- CSRF misuse and replay
- Input validation bypass attempts
- Size and flood abuse
- Host/CORS misconfiguration exposure
- Traversal/injection style payload handling

## 9. CI and Pre-commit

CI workflow is in `.github/workflows/ci.yml`.

It currently enforces:

- formatting (`ruff format`, `rumdl fmt`, then no diff)
- lint/type/test
- API coverage gate (100% on `app/api`)
- markdown checks
- Jx catalog check

Local pre-commit config:

- `.pre-commit-config.yaml`

Recommended local command before commit:

- `task ci`

## 10. Docker and Deployment

Use:

- Dev: `docker/docker-compose.yml` + `docker/Dockerfile.dev`
- Prod: `docker/docker-compose.prod.yml` + `docker/Dockerfile.prod`

Traefik:

- Static config: `docker/traefik/traefik.yml`
- Dynamic config: `docker/traefik/dynamic/routing.yml`

Do not move routing logic back into compose labels unless explicitly required.

## 11. Documentation Policy

If architecture, security, infra, or design changes, update docs in the same
change set:

- `docs/architecture.md`
- `docs/backend.md`
- `docs/frontend.md`
- `docs/infrastructure.md`
- `docs/security.md`
- `docs/design-system.md`
- `docs/figma-tokens.md`

Main docs index:

- `docs/README.md`

Project overview:

- `README.md` (keep concise and link to docs)

## 12. Commit and PR Guidelines

- Prefer small commits by concern/type:
  - `feat:`
  - `fix:`
  - `refactor:`
  - `test:`
  - `docs:`
  - `chore:`
- Do not commit temporary TODO scratch files.
- Keep unrelated refactors out of feature/security fixes.
- Include test updates with behavior changes.

## 13. Agent Execution Checklist

Before starting:

1. Read `README.md` and `docs/README.md`.
2. Confirm target files and impact scope.

Before finishing:

1. Run formatting/lint/tests.
2. Validate route/security behavior for changed endpoints.
3. Update docs if behavior/contracts changed.
4. Provide a concise change summary with file references.
