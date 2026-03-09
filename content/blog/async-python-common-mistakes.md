---
title: "Async Python: Common Mistakes"
slug: "async-python-common-mistakes"
description: "Mistakes that turn async code into something slower than its synchronous equivalent."
date: "2026-01-10"
author: "Fabio Souza"
tags:
  - "python"
  - "async"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Async Python is genuinely useful for I/O-heavy workloads. It is also easy to
misuse in ways that are hard to diagnose.

## Blocking calls inside coroutines

The most common mistake is calling a blocking function inside an `async def`.

```python
async def get_user(user_id: int) -> User:
    # This blocks the entire event loop
    return db.query(User).filter_by(id=user_id).one()
```

Use `asyncio.to_thread` to offload blocking work or switch to an async driver.

## Forgetting to await

A coroutine that is not awaited returns a coroutine object silently. Static
analysis tools like `mypy` with `asyncio` plugins will catch this, but it is
easy to miss in code review.

## Spawning too many tasks at once

`asyncio.gather` without a semaphore will open as many connections as you have
tasks. Add a `asyncio.Semaphore` to bound concurrency when hitting external
services.

## Shared mutable state

Async code is still single-threaded in Python but concurrent in execution.
Mutating shared lists or dicts between awaits is safe, but mixing asyncio
with threading introduces real race conditions.
