---
title: "Clean Architecture Notes From Real Projects"
slug: "clean-architecture-notes-from-real-projects"
description: "Patterns that keep web projects maintainable after the first release."
date: "2026-01-29"
author: "Fabio Souza"
tags:
  - "architecture"
  - "python"
  - "backend"
featured: true
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

The most useful architecture rule in day-to-day work is simple:

> Routers should translate HTTP, services should hold behavior.

When route files stay thin, tests become cheaper and refactors are safer.

## Heuristics I use

- If logic depends on business terms, it belongs in a service/use-case.
- If logic depends on headers or status codes, it belongs in the router layer.
- If many pages use the same data contract, define a typed context model once.

This keeps templates predictable and avoids hidden coupling across folders.

## Where boundaries pay off first

The first place architecture pays for itself is not scale. It is change.

When a contact flow starts simple, it is tempting to keep validation, email
delivery, analytics, and response mapping in one route function. That works
for a week. Then the second notification channel appears, rate limiting changes,
and someone asks for better telemetry around failures.

If the route is only responsible for HTTP concerns, the shape of that change is
clear:

- router validates transport details
- service decides the use-case path
- infrastructure handles side effects
- rendering maps output into a stable page contract

That separation does not remove complexity. It puts complexity where it can be
tested with less friction.

## The mistakes I try to avoid

Most architecture drift comes from three repeated mistakes.

First, business rules get attached to framework objects. A service that needs
`Request`, `Response`, or raw headers usually becomes harder to reuse and harder
to reason about.

Second, templates become implicit contracts. If the page silently expects ten
variables with loose names, small UI changes become risky because nothing tells
you what the page actually requires.

Third, "utility" modules become dumping grounds. Shared helpers are useful, but
only when they stay generic. The moment they encode a workflow, they are no
longer helpers; they are hidden services.

## Template contracts matter more than they look

Server-rendered apps stay maintainable when rendering data is typed and boring.

I prefer a page context model that answers a simple question: what does this
page need, and nothing else? That sounds obvious, but it changes how teams work.

Instead of passing broad dictionaries into templates, typed page contexts make
each page explicit:

- title, metadata, and navigation state are visible in one place
- optional fields are intentional instead of accidental
- missing values fail early during development

For personal sites, docs, and admin apps, this approach removes a surprising amount
of UI confusion.

## Service boundaries and telemetry

Another practical benefit is observability.

If a service boundary already exists, instrumentation gets easier. You can log
use-case outcomes, attach span names around meaningful operations, and record
metrics at the level people actually discuss incidents.

That is better than only having "POST /contact returned 500".

Useful signals usually look like:

- contact submission accepted
- contact notification delivery failed
- markdown parsing skipped invalid document
- page rendering completed with empty content fallback

Those names are understandable during incidents, code review, and dashboard work.

## A lightweight review checklist

When I review a new feature, I usually ask:

1. Is the router still thin?
2. Does the service own the business decision?
3. Are side effects isolated?
4. Is the page contract typed and explicit?
5. Can telemetry describe the outcome in domain language?

If those answers are clear, the codebase usually stays flexible without turning
into ceremony.

Clean architecture only becomes a problem when it is performed like theater.
Used carefully, it simply reduces the cost of the next change.
