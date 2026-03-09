---
title: "FastAPI Observability Playbook"
slug: "fastapi-observability-playbook"
description: "A practical checklist for traces, metrics, logs, and alert signals in FastAPI services."
date: "2026-02-18"
author: "Fabio Souza"
tags:
  - "fastapi"
  - "observability"
  - "opentelemetry"
featured: true
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Good observability starts with **consistent naming** and **clear ownership**.

In FastAPI applications, I keep three layers instrumented:

1. Request lifecycle (latency, status code, route)
2. Use-case boundaries (business outcomes)
3. Integrations (email, webhooks, databases, external APIs)

A simple rule works well: if an endpoint fails in production, you should be
able to answer _what failed, where, and for whom_ in under five minutes.

## What to instrument first

- Request duration and status code per route
- Error class frequency
- Contact/API abuse signals (rate limits, body size violations)
- Outbound dependency latency and failure ratio

With this baseline, adding dashboards and alerts becomes straightforward.

## The signal hierarchy I use

I treat traces, metrics, and logs as different tools, not interchangeable ones.

Metrics tell me if the system is drifting. Traces tell me where time is going.
Logs explain the local facts around one event. The mistake is expecting one of
them to carry the whole incident alone.

For a FastAPI service, the basic split is:

- metrics for route latency, throughput, error ratios, and dependency health
- traces for request flow and expensive downstream calls
- logs for validation failures, state transitions, and operator context

That keeps each signal type small enough to stay useful.

## What a healthy trace shape looks like

I want traces to tell a short story.

A request span should identify the route template and status code. Nested spans
should represent use-case work and outbound dependencies, not every internal
function call. If a trace becomes a stack dump, it loses diagnostic value.

For example, a contact submission request might look like:

1. HTTP span for `POST /contact`
2. validation/use-case span
3. webhook delivery span
4. email delivery span

That is enough to spot slow paths, retry pain, and external failures.

## Logs that survive a real incident

Logs are still the quickest way to answer "what exactly happened?"

The main thing I avoid is unstructured debug noise. If every line is free-form,
incident review becomes expensive. I prefer logs that preserve a few stable
fields:

- request id
- route
- outcome
- relevant resource id or slug
- exception type when something failed

The message can stay human. The fields need to stay predictable.

## Alerts I actually keep

Most bad alerting starts from monitoring everything at the same severity.

I prefer a short list of alerts that imply action:

- sustained route error ratio above a threshold
- dependency latency p95 or p99 drifting beyond baseline
- contact or analytics abuse controls firing unusually often
- queue or delivery backlogs growing without recovery

If an alert does not change behavior, it should probably be a dashboard instead.

## What I delay on purpose

Not every service needs deep observability on day one.

I usually delay:

- custom business metrics with no current operator use
- detailed span attributes that nobody queries
- logs that duplicate trace information
- dashboards for flows that rarely change

The first goal is fast diagnosis, not a museum of charts.

## A practical rollout order

If I am instrumenting an existing FastAPI service, this is usually the order:

1. request ids and trace correlation in logs
2. route latency and error metrics
3. dependency spans and failure counters
4. abuse/security-related metrics
5. focused alerts tied to operator decisions

That sequence gives usable feedback quickly without dragging the whole team into
observability work for weeks.
