---
title: "Redis Cache Patterns That Actually Work"
slug: "redis-cache-patterns"
description: "Cache-aside, write-through, and TTL strategies for backend services using Redis."
date: "2025-10-20"
author: "Fabio Souza"
tags:
  - "redis"
  - "caching"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Redis is simple to add and easy to misuse. The patterns below cover the common
use cases and the failure modes worth knowing upfront.

## Cache-aside (lazy loading)

The application checks the cache before hitting the database. On a miss, it
fetches from the database, stores the result, and returns it.

This is the safest default pattern. It only caches data that is actually read.

## Write-through

On every database write, also update the cache. Keeps the cache warm and
consistent but adds latency to writes.

Use this when reads are very frequent and cache misses are expensive.

## TTL strategy

Every key should have a TTL. Unbounded caches grow until Redis evicts entries
under memory pressure, which is unpredictable. Set TTLs based on how stale
the data can be, not on arbitrary defaults.

## Thundering herd on cache expiry

When a popular key expires, many concurrent requests hit the database
simultaneously. Mitigate with probabilistic early expiration or a distributed
lock that lets one request regenerate the cache while others wait.

## Key naming convention

Use a consistent prefix scheme: `{service}:{entity}:{id}` (e.g.,
`api:user:1234`). Prefix-based deletion with `SCAN` is easier to operate.
