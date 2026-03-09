---
title: "Postgres Query Patterns for Backend Devs"
slug: "postgres-query-patterns-for-backend-devs"
description: "Practical query techniques that improve throughput without over-engineering the schema."
date: "2026-02-05"
author: "Fabio Souza"
tags:
  - "postgres"
  - "backend"
  - "python"
featured: false
discussion_url: "https://github.com/oornnery/proj/portfolio/discussions"
---

The queries that slow down a system are rarely the obvious ones. They hide behind
N+1 loops, missing indexes on foreign keys, and `SELECT *` in hot paths.

## Always index what you filter on

Foreign key columns are not automatically indexed in Postgres. If you join or
filter on `user_id` regularly, add the index explicitly.

```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

## Use EXPLAIN ANALYZE before optimizing

Gut feeling is unreliable. Run `EXPLAIN (ANALYZE, BUFFERS)` and look at
sequential scans and row estimates before touching the schema.

## Prefer CTEs for readability, not always for performance

Postgres materializes CTEs differently depending on version and query planner
hints. In most cases, a subquery inside a `WHERE` clause gives the planner more
freedom to optimize.

## Avoid SELECT * in application code

Fetching unnecessary columns increases network overhead and breaks caching
assumptions. Name your columns explicitly and add only what the caller needs.
