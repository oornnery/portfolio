---
title: "Secure Contact Pipeline"
slug: "secure-contact-pipeline"
description: >-
  A contact flow with CSRF protection, strict validation, anti-spam limits, and
  decoupled notifications.
thumbnail: "/static/images/projects/secure-contact-pipeline.svg"
tags: ["security", "fastapi", "webhooks"]
tech_stack: ["FastAPI", "Pydantic", "SlowAPI", "HTTPX"]
github_url: "https://github.com/oornnery/secure-contact-pipeline"
live_url: "https://example.dev/secure-contact-pipeline"
date: 2025-08-03
featured: true
---

## Overview

This project demonstrates a secure form submission workflow with clear backend
responsibilities.
The router is intentionally thin, while use-case services perform validation
and orchestration.

## Security controls

- HMAC-signed CSRF token with expiration
- Field-level validation using Pydantic models
- Rate limiting per client IP
- Strict security headers middleware

## Architecture

Notification delivery is isolated in channels.
The same submission can be delivered to webhook and email without coupling the
HTTP layer.
