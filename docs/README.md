# Portfolio Documentation

This folder centralizes the technical documentation of the project.

## Summary

1. [Architecture](architecture.md)
2. [Backend](backend.md)
3. [Frontend](frontend.md)
4. [Infrastructure](infrastructure.md)
5. [Security](security.md)
6. [Design System](design-system.md)
7. [Figma Tokens and Handoff](figma-tokens.md)

## Recommended Reading Order

1. Start with [Architecture](architecture.md) for the full system map.
2. Read [Backend](backend.md) and [Frontend](frontend.md)
   for implementation details.
3. Continue with [Infrastructure](infrastructure.md)
   and [Security](security.md) for deployment and hardening.
4. Finish with [Design System](design-system.md)
   and [Figma Tokens and Handoff](figma-tokens.md)
   for UI consistency.

## Source of Truth

The docs were derived from the current implementation in:

- `app/main.py`
- `app/api/*`
- `app/services/*`
- `app/core/security.py`
- `app/core/config.py`
- `app/components/*`
- `app/static/css/*`
- `app/static/js/*`
- `docker/*`
- `infra/*`
- `tests/test_routes_api_coverage.py`
- `tests/test_security_owasp.py`
