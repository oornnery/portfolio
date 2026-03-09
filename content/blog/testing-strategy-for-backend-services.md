---
title: "Testing Strategy for Backend Services"
slug: "testing-strategy-for-backend-services"
description: "A practical layered approach to backend tests: what to unit test, what to integrate, and what to skip."
date: "2025-07-30"
author: "Fabio Souza"
tags:
  - "testing"
  - "python"
  - "backend"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Good test coverage is not about hitting a percentage target. It is about having
confidence that the important paths work and that regressions are caught fast.

## Unit tests belong on business logic

Services, validators, and domain rules are the right target for unit tests.
They run fast, are easy to isolate, and catch the logic bugs that matter most.

```python
def test_normalize_tag_strips_whitespace():
    assert normalize_tag("  python  ") == "python"
```

## Integration tests belong on the HTTP boundary

Test routes with a real (test) database or in-memory equivalents. Focus on
correct status codes, response shapes, and side effects.

Use `httpx.AsyncClient` with FastAPI's ASGI transport for clean, fast HTTP
integration tests that do not require a running server.

## Skip tests for third-party code

Do not write tests that only verify that a library works correctly. Trust the
library, test your use of it.

## Property-based testing for edge cases

Libraries like `hypothesis` generate inputs that reveal edge cases you would
not think to write manually. Useful for parsers, validators, and math-heavy
functions.

## Keep the test pyramid healthy

Many unit tests, fewer integration tests, minimal end-to-end tests. End-to-end
tests are expensive to write and flaky to run.
