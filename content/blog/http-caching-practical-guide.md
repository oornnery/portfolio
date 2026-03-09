---
title: "HTTP Caching: A Practical Guide"
slug: "http-caching-practical-guide"
description: "Cache-Control, ETags, and stale-while-revalidate explained with real backend examples."
date: "2025-12-15"
author: "Fabio Souza"
tags:
  - "http"
  - "caching"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/portfolio/discussions"
---

HTTP caching is one of the highest-leverage performance tools available. Most
backend teams underuse it because the header semantics are confusing.

## Cache-Control directives that matter

- `max-age=N` — browser caches for N seconds
- `s-maxage=N` — CDN caches for N seconds, overrides `max-age` for shared caches
- `no-cache` — always revalidate before using cached copy
- `no-store` — never cache (use for sensitive data)
- `stale-while-revalidate=N` — serve stale while fetching fresh in background

## ETags for conditional requests

An ETag is a version token for a resource. Clients send `If-None-Match` with
the stored ETag; servers reply with `304 Not Modified` if nothing changed.

```python
from hashlib import md5

def etag_for(content: str) -> str:
    return f'"{md5(content.encode()).hexdigest()}"'
```

## What to cache aggressively

Static assets with content-hashed filenames: `max-age=31536000, immutable`.
API responses that change rarely: `max-age=60, stale-while-revalidate=300`.

## What not to cache

User-specific data, CSRF tokens, and anything with `Authorization`-gated access
should be `Cache-Control: private, no-store`.
