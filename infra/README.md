# Infrastructure Observability Assets

This directory stores operational observability artifacts for SigNoz.
Grafana- and Prometheus-specific assets were removed from this repository.

## Contents

- `signoz/dashboards/site-unified-operations.json`
  - Unified operations dashboard spanning backend health, frontend telemetry,
    contact flow, and OTLP proxy health in one view.
- `signoz/dashboards/site-backend-overview.json`
  - Backend service operations dashboard: traffic, latency, errors, top routes,
    contact flow, notifications, and OTLP proxy health.
- `signoz/dashboards/site-frontend-telemetry.json`
  - Frontend telemetry dashboard: lifecycle spans, user interactions, contact
    form flow, client errors, and OTLP proxy health.
- `signoz/alerts/*.json`
  - Alert rule manifests for backend errors/latency, notification latency,
    contact delivery degradation, frontend error rate, document load latency,
    and OTLP proxy failures.
- `signoz/README.md`
  - Import runbook for dashboards and alerts.

## Runtime dependencies

These assets assume the application is exporting telemetry through
OpenTelemetry via `opentelemetry-instrument`.

## SigNoz setup (logs, metrics, traces)

Configure the application environment with OTLP endpoint values.

For local SigNoz (default OTLP gRPC):

```env
OTEL_SERVICE_NAME=site-backend
OTEL_RESOURCE_ATTRIBUTES=service.namespace=site,deployment.environment=development
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_EXPORTER_OTLP_INSECURE=true
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
FRONTEND_TELEMETRY_ENABLED=true
```

For SigNoz Cloud, include auth headers:

```env
OTEL_SERVICE_NAME=site-backend
OTEL_RESOURCE_ATTRIBUTES=service.namespace=site,deployment.environment=production
OTEL_EXPORTER_OTLP_ENDPOINT=https://ingest.<region>.signoz.cloud:443
OTEL_EXPORTER_OTLP_INSECURE=false
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
FRONTEND_TELEMETRY_ENABLED=true
OTEL_EXPORTER_OTLP_HEADERS=signoz-ingestion-key=<your-key>
```

## Validation checklist

1. Start the app and hit `/`, `/about`, `/projects`, `/contact`.
2. Open SigNoz and confirm services `site-backend` and
   `site-frontend` appear.
3. Verify traces, metrics, and logs are ingesting.
4. Confirm `POST /otel/v1/traces` traffic appears in the frontend dashboard.
5. Import the dashboards and alerts from `infra/signoz/`.

Detailed import instructions live in `infra/signoz/README.md`.

## Refs

- OpenTelemetry Python docs:
  <https://opentelemetry.io/docs/languages/python/>
- OpenTelemetry JS docs:
  <https://opentelemetry.io/docs/languages/js/>
- SigNoz dashboards repo:
  <https://github.com/SigNoz/dashboards>
- SigNoz API docs:
  <https://github.com/SigNoz/signoz/blob/main/docs/api/openapi.yml>
