import logging
from typing import Any

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

from app.config import settings

logger = logging.getLogger(__name__)

otlp_metric_exporter_factory: Any | None = None
otlp_span_exporter_factory: Any | None = None

try:
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
    )
    otlp_metric_exporter_factory = OTLPMetricExporter
    otlp_span_exporter_factory = OTLPSpanExporter
except Exception:  # pragma: no cover
    otlp_metric_exporter_factory = None
    otlp_span_exporter_factory = None

_configured = False


def _build_resource() -> Resource:
    return Resource.create(
        {
            "service.name": settings.telemetry_service_name,
            "service.namespace": settings.telemetry_service_namespace,
            "deployment.environment": "development" if settings.debug else "production",
        }
    )


def _configure_tracing(resource: Resource) -> None:
    sampler = ParentBased(TraceIdRatioBased(settings.telemetry_traces_sample_ratio))
    tracer_provider = TracerProvider(resource=resource, sampler=sampler)

    if settings.telemetry_exporter_otlp_endpoint and otlp_span_exporter_factory is not None:
        span_exporter = otlp_span_exporter_factory(
            endpoint=settings.telemetry_exporter_otlp_endpoint,
            insecure=settings.telemetry_exporter_otlp_insecure,
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
        logger.info(
            f"Tracing exporter configured with OTLP endpoint={settings.telemetry_exporter_otlp_endpoint}."
        )
    elif settings.telemetry_console_exporters:
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        logger.info("Tracing exporter configured with console output.")

    trace.set_tracer_provider(tracer_provider)


def _configure_metrics(resource: Resource) -> None:
    metric_readers: list[Any] = []
    if settings.telemetry_exporter_otlp_endpoint and otlp_metric_exporter_factory is not None:
        metric_exporter = otlp_metric_exporter_factory(
            endpoint=settings.telemetry_exporter_otlp_endpoint,
            insecure=settings.telemetry_exporter_otlp_insecure,
        )
        metric_readers.append(PeriodicExportingMetricReader(metric_exporter))
        logger.info(
            f"Metric exporter configured with OTLP endpoint={settings.telemetry_exporter_otlp_endpoint}."
        )
    elif settings.telemetry_console_exporters:
        metric_readers.append(
            PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=15000)
        )

    meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
    metrics.set_meter_provider(meter_provider)


def configure_telemetry(app: FastAPI) -> None:
    global _configured
    if _configured:
        return

    if not settings.telemetry_enabled:
        logger.info("Telemetry is disabled by configuration.")
        return

    resource = _build_resource()
    _configure_tracing(resource)
    _configure_metrics(resource)

    FastAPIInstrumentor.instrument_app(app, excluded_urls="/static,/favicon.ico")
    HTTPXClientInstrumentor().instrument()

    _configured = True
    logger.info("OpenTelemetry configured successfully.")


def get_tracer(name: str):
    return trace.get_tracer(name)


def get_meter(name: str):
    return metrics.get_meter(name)
