# Observability Runbook

This project emits telemetry through OpenTelemetry and provides starter
artifacts for dashboards and alerts.

## Artifacts

- Grafana dashboard:
  - `infra/grafana/portfolio-overview-dashboard.json`
- Prometheus alert rules:
  - `infra/alerts/portfolio-alert-rules.yaml`

## Correlation fields

All request logs include:

- `req_id` (application request id)
- `trace_id` (OpenTelemetry trace id)
- `span_id` (OpenTelemetry span id)
- `method`, `path`, `ip`

Use those fields to jump between logs and traces.

## Metrics exposed through OTel meter

- `portfolio.http.requests_total`
- `portfolio.http.request_duration_ms`
- `portfolio.http.requests_in_flight`
- `portfolio.contact.submissions_total`
- `portfolio.contact.notification_total`
- `portfolio.contact.notification_duration_ms`
- `portfolio.analytics.events_total`
- `portfolio.analytics.events_rejected_total`

When exported to Prometheus-compatible backends, names are typically normalized
to underscore form (for example, `portfolio_http_requests_total`).

## Example queries

### Error ratio (5xx)

```promql
sum(rate(portfolio_http_requests_total{status_code=~"5.."}[5m]))
/
clamp_min(sum(rate(portfolio_http_requests_total[5m])), 1)
```

### p95 latency

```promql
histogram_quantile(
  0.95,
  sum by (le) (rate(portfolio_http_request_duration_ms_bucket[5m]))
)
```

### Contact outcomes

```promql
sum by (outcome) (rate(portfolio_contact_submissions_total[5m]))
```

### Analytics accepted by event type

```promql
sum by (event_name) (rate(portfolio_analytics_events_total[5m]))
```

## Local debug tips

- Enable console telemetry exporters in `.env`:
  - `TELEMETRY_CONSOLE_EXPORTERS=true`
- Keep tracing enabled:
  - `TELEMETRY_ENABLED=true`
- Run app:
  - `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

This gives quick local visibility for spans and metric emissions.

## SigNoz setup (logs + metrics + traces)

This project exports telemetry to SigNoz through OTLP gRPC. Configure these
variables in `.env`:

```env
TELEMETRY_ENABLED=true
TELEMETRY_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
TELEMETRY_EXPORTER_OTLP_INSECURE=true
TELEMETRY_LOGS_ENABLED=true
# Optional (SigNoz Cloud or custom gateway auth header):
# TELEMETRY_EXPORTER_OTLP_HEADERS=signoz-ingestion-key=<your-key>
```

### What is exported

- Traces: OpenTelemetry spans from FastAPI and HTTPX.
- Metrics: application metrics registered in `app/observability/metrics.py`.
- Logs: Python logs routed through OpenTelemetry `LoggingHandler`.

### Validation checklist

- Start the app:
  - `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Hit the app routes (`/`, `/about`, `/projects`, `/contact`).
- In SigNoz UI, validate:
  - service appears as `portfolio-backend`
  - traces are visible for incoming HTTP requests
  - metrics are populated (request counters/histograms)
  - logs are visible and correlate by trace ID
