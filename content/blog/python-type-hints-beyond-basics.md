---
title: "Python Type Hints Beyond the Basics"
slug: "python-type-hints-beyond-basics"
description: "TypeVar, Protocol, TypedDict, and Annotated for teams that want real static guarantees."
date: "2025-11-05"
author: "Fabio Souza"
tags:
  - "python"
  - "types"
  - "architecture"
featured: false
discussion_url: "https://github.com/oornnery/proj/portfolio/discussions"
---

Basic type hints (`str`, `int`, `list[str]`) get you most of the way. Beyond
that, a few advanced features close the remaining gaps.

## Protocol for structural typing

`Protocol` lets you define interfaces without inheritance. Any class that
implements the required methods satisfies the protocol.

```python
from typing import Protocol

class Notifier(Protocol):
    def send(self, message: str) -> None: ...
```

This is more flexible than ABC and works with third-party classes you cannot
modify.

## TypeVar for generic functions

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

## TypedDict for dict-shaped data

When you need to annotate a dict without converting it to a dataclass or Pydantic
model, `TypedDict` gives you field-level checking.

## Annotated for metadata

`Annotated[int, Gt(0)]` lets libraries like Pydantic and FastAPI attach
validation metadata to type annotations without changing the underlying type.
