import logging
from typing import Any

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

from app.core.config import settings

logger = logging.getLogger(__name__)

otlp_metric_exporter_factory: Any | None = None
otlp_log_exporter_factory: Any | None = None
otlp_span_exporter_factory: Any | None = None
otel_batch_log_record_processor_factory: Any | None = None
otel_console_log_exporter_factory: Any | None = None
otel_logger_provider_factory: Any | None = None
otel_logging_handler_factory: Any | None = None
otel_set_logger_provider: Any | None = None

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

try:
    from opentelemetry import _logs as otel_logs
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import (
        BatchLogRecordProcessor,
        ConsoleLogRecordExporter,
    )

    otlp_log_exporter_factory = OTLPLogExporter
    otel_batch_log_record_processor_factory = BatchLogRecordProcessor
    otel_console_log_exporter_factory = ConsoleLogRecordExporter
    otel_logger_provider_factory = LoggerProvider
    otel_logging_handler_factory = LoggingHandler
    otel_set_logger_provider = otel_logs.set_logger_provider
except Exception:  # pragma: no cover
    otlp_log_exporter_factory = None
    otel_batch_log_record_processor_factory = None
    otel_console_log_exporter_factory = None
    otel_logger_provider_factory = None
    otel_logging_handler_factory = None
    otel_set_logger_provider = None

_configured = False
_otel_log_handler_attached = False


def _otlp_headers() -> str | None:
    headers = settings.telemetry_exporter_otlp_headers.strip()
    return headers if headers else None


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
    headers = _otlp_headers()

    if (
        settings.telemetry_exporter_otlp_endpoint
        and otlp_span_exporter_factory is not None
    ):
        span_exporter = otlp_span_exporter_factory(
            endpoint=settings.telemetry_exporter_otlp_endpoint,
            insecure=settings.telemetry_exporter_otlp_insecure,
            headers=headers,
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
    headers = _otlp_headers()
    if (
        settings.telemetry_exporter_otlp_endpoint
        and otlp_metric_exporter_factory is not None
    ):
        metric_exporter = otlp_metric_exporter_factory(
            endpoint=settings.telemetry_exporter_otlp_endpoint,
            insecure=settings.telemetry_exporter_otlp_insecure,
            headers=headers,
        )
        metric_readers.append(PeriodicExportingMetricReader(metric_exporter))
        logger.info(
            f"Metric exporter configured with OTLP endpoint={settings.telemetry_exporter_otlp_endpoint}."
        )
    elif settings.telemetry_console_exporters:
        metric_readers.append(
            PeriodicExportingMetricReader(
                ConsoleMetricExporter(), export_interval_millis=15000
            )
        )

    meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
    metrics.set_meter_provider(meter_provider)


def _configure_logs(resource: Resource) -> None:
    global _otel_log_handler_attached
    if not settings.telemetry_logs_enabled:
        logger.info("Telemetry log export is disabled by configuration.")
        return

    if (
        otel_set_logger_provider is None
        or otel_logger_provider_factory is None
        or otel_batch_log_record_processor_factory is None
        or otel_logging_handler_factory is None
    ):
        logger.warning(
            "OpenTelemetry logging dependencies are unavailable; log export is disabled."
        )
        return

    logger_provider = otel_logger_provider_factory(resource=resource)
    headers = _otlp_headers()
    exporter_configured = False

    if (
        settings.telemetry_exporter_otlp_endpoint
        and otlp_log_exporter_factory is not None
    ):
        log_exporter = otlp_log_exporter_factory(
            endpoint=settings.telemetry_exporter_otlp_endpoint,
            insecure=settings.telemetry_exporter_otlp_insecure,
            headers=headers,
        )
        logger_provider.add_log_record_processor(
            otel_batch_log_record_processor_factory(log_exporter)
        )
        exporter_configured = True
        logger.info(
            f"Log exporter configured with OTLP endpoint={settings.telemetry_exporter_otlp_endpoint}."
        )
    elif (
        settings.telemetry_console_exporters
        and otel_console_log_exporter_factory is not None
    ):
        logger_provider.add_log_record_processor(
            otel_batch_log_record_processor_factory(otel_console_log_exporter_factory())
        )
        exporter_configured = True
        logger.info("Log exporter configured with console output.")

    if not exporter_configured:
        logger.info(
            "Telemetry log exporter is not configured; OTLP endpoint is empty and console exporters are disabled."
        )
        return

    otel_set_logger_provider(logger_provider)
    if not _otel_log_handler_attached:
        root_logger = logging.getLogger()
        root_logger.addHandler(
            otel_logging_handler_factory(
                level=logging.NOTSET,
                logger_provider=logger_provider,
            )
        )
        _otel_log_handler_attached = True
        logger.info("OpenTelemetry logging handler attached to root logger.")


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
    _configure_logs(resource)

    FastAPIInstrumentor.instrument_app(app, excluded_urls="/static,/favicon.ico")
    HTTPXClientInstrumentor().instrument()

    _configured = True
    logger.info("OpenTelemetry configured successfully.")


def get_tracer(name: str):
    return trace.get_tracer(name)


def get_meter(name: str):
    return metrics.get_meter(name)
