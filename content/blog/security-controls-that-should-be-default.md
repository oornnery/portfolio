---
title: "Security Controls That Should Be Default"
slug: "security-controls-that-should-be-default"
description: "A baseline set of controls that prevents common web abuse patterns early."
date: "2025-12-11"
author: "Fabio Souza"
tags:
  - "security"
  - "owasp"
  - "fastapi"
featured: true
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Security hardening is easier when controls are default behavior, not optional add-ons.

For small and medium services, this baseline already blocks many incidents:

- CSRF token generation + validation for forms
- Strict content-type checks
- Body size limits by route sensitivity
- Global and route-specific rate limits
- Trusted hosts + CORS allowlist
- Consistent security headers and CSP

The goal is not perfection. The goal is to eliminate low-effort attack paths early.

## Defaults beat policy documents

Security drift usually happens when protection depends on remembering to turn it
on. A control that requires every feature author to opt in will eventually be
missed under time pressure.

That is why I prefer secure defaults wired into the application shell:

- middleware for headers and host validation
- shared form protection for CSRF-sensitive flows
- body limits enforced before heavy work starts
- dependency wiring that centralizes allowlists and rate limits

This changes security from "please remember" to "you have to bypass it on purpose."

## Controls that stop common abuse early

For personal or product sites, the most common issues are rarely exotic.

They are usually:

- spam against contact flows
- oversized request bodies
- origin and host header mistakes
- analytics endpoints abused as open collectors
- weak content sanitization for markdown or rich text

Good defaults dramatically reduce these paths before they become incidents.

## Split edge and app responsibilities clearly

I do not want the app and proxy fighting for the same job without intent.

At the edge, I want broad traffic shaping:

- connection and in-flight caps
- coarse body size controls
- broad rate limiting
- IP-based allowlists when required

In the app, I want context-aware protection:

- route-specific body limits
- CSRF validation
- trusted hosts
- content-type enforcement
- response headers and content sanitization

That split keeps enforcement layered but understandable.

## Validation should fail explicitly

A subtle security problem is vague failure behavior.

If malformed input, missing CSRF tokens, and unsupported content types all
collapse into the same generic handling, it becomes harder to debug abuse and
harder to reason about protections.

I prefer stable, explicit failure paths with predictable status codes and logs.
That helps both defenders and maintainers without exposing sensitive internals.

## Review the baseline like product code

Security controls are product behavior. They need review the same way business
features do.

My quick baseline review looks like this:

1. Can an unsafe host reach the app?
2. Can a large or malformed body bypass route intent?
3. Can a form post succeed without a valid CSRF token?
4. Can markdown or HTML content render unsafe elements?
5. Can abuse against analytics or contact routes be throttled?

If those answers are visible in tests and code structure, the baseline tends to
stay strong over time.

The point is not to create a fortress around a simple site. The point is to make
common abuse paths expensive from the start.
