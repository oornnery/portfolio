# ADR 0001: CSP and Asset Loading Strategy

- Status: Accepted
- Date: 2026-02-26

## Context

The application serves HTML with server-rendered Jx components and relies on
shared static assets. Security hardening requires a strict Content Security
Policy (CSP), while developer workflow still needs practical local feedback.

## Decision

- Enforce strict CSP in non-debug environments:
  - `default-src 'self'`
  - `script-src 'self'`
  - `style-src 'self'`
  - `img-src 'self' data: https:`
  - `font-src 'self' https:`
  - `connect-src 'self'`
  - `object-src 'none'`
  - `frame-src 'none'`
  - `form-action 'self'`
- Avoid inline scripts/styles in templates.
- Keep runtime assets loaded from local `/static/*`.

## Consequences

- Better default security posture and reduced XSS blast radius.
- Template authors must avoid inline script/style blocks.
- Any future third-party script inclusion must be explicitly justified.
