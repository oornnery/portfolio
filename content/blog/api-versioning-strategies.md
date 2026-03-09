---
title: "API Versioning Strategies"
slug: "api-versioning-strategies"
description: "URL path, header, and query-param versioning compared — with practical trade-offs for each."
date: "2025-08-28"
author: "Fabio Souza"
tags:
  - "api"
  - "architecture"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/portfolio/discussions"
---

Every public API eventually needs versioning. Choosing the right strategy early
avoids painful migrations later.

## URL path versioning

```text
GET /v1/users
GET /v2/users
```

The most visible and cache-friendly option. Clients can bookmark or hardcode
URLs. The downside is that the version pollutes every route.

## Header versioning

```text
GET /users
API-Version: 2024-01-01
```

Keeps URLs clean. Harder to test in a browser or share as a link. Common in
Stripe and GitHub APIs.

## Query parameter

```text
GET /users?version=2
```

Easy to add and test but often treated as an afterthought. Caching is more
complex because the cache key must include the param.

## What matters more than the strategy

Consistency and a clear deprecation policy. Pick one approach, document it,
and give clients enough notice before removing old versions. Most teams
underinvest in deprecation communication and overinvest in version strategy.
