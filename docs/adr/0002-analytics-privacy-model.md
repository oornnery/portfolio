# ADR 0002: Analytics Privacy Model and Event Contract

- Status: Accepted
- Date: 2026-02-26

## Context

The frontend emits behavior events and the backend ingests them for
observability. We need analytics useful for product insight without collecting
sensitive personal data.

## Decision

- Use a typed server-side schema for analytics events.
- Accept only explicit event names and structured payloads.
- Redact or hash sensitive values before logs/traces.
- Use declarative frontend hooks (`data-analytics-*`) instead of broad DOM
  scraping/fingerprinting.
- Treat event ingestion as best-effort telemetry, not business-critical data.

## Consequences

- Lower privacy risk and clearer compliance story.
- Easier operational debugging due to consistent event shape.
- New event types require schema updates and explicit rollout.
