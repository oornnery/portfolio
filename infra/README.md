# Infrastructure Observability Assets

This directory stores operational observability artifacts used by dashboards
and alerting tools.

## Contents

- `grafana/portfolio-overview-dashboard.json`
  - Grafana dashboard definition for the portfolio service.
- `alerts/portfolio-alert-rules.yaml`
  - Alert rules intended for Prometheus-compatible alert managers.

## How to use

### Grafana dashboard

1. Open Grafana and go to Dashboard import.
2. Import `infra/grafana/portfolio-overview-dashboard.json`.
3. Bind the dashboard to your metrics datasource.

### Alert rules

1. Add `infra/alerts/portfolio-alert-rules.yaml` to your Prometheus rules path.
2. Reload or restart the Prometheus server.
3. Confirm alert groups are active in your alerting UI.

## Runtime dependencies

These files assume the application is exporting telemetry (metrics/logs/traces)
through OpenTelemetry, as configured in the app settings.

## SigNoz setup (logs, metrics, traces)

Configure the application environment with OTLP endpoint values.

For local SigNoz (default OTLP gRPC):

```env
TELEMETRY_ENABLED=true
TELEMETRY_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
TELEMETRY_EXPORTER_OTLP_INSECURE=true
TELEMETRY_LOGS_ENABLED=true
```

For SigNoz Cloud, include auth headers:

```env
TELEMETRY_ENABLED=true
TELEMETRY_EXPORTER_OTLP_ENDPOINT=https://ingest.<region>.signoz.cloud:443
TELEMETRY_EXPORTER_OTLP_INSECURE=false
TELEMETRY_LOGS_ENABLED=true
TELEMETRY_EXPORTER_OTLP_HEADERS=signoz-ingestion-key=<your-key>
```

### Validation checklist (SigNoz)

1. Start the app and hit `/`, `/about`, `/projects`, `/contact`.
2. Open SigNoz and confirm service `portfolio-backend` appears.
3. Verify traces, metrics, and logs are all being ingested.
4. Confirm logs can be correlated by trace ID.

This file is the primary runbook for observability setup in this repository.

## Refs

- OpenTelemetry Python docs:
  <https://opentelemetry.io/docs/languages/python/>
- Grafana dashboard import docs:
  <https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/import-dashboards/>
- Prometheus alerting rules docs:
  <https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/>
