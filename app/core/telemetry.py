"""
OpenTelemetry Integration for Portfolio Application.

Why: Observabilidade completa com traces distribuídos,
     métricas e logs correlacionados.

How: Configura OpenTelemetry SDK com exporters para
     console (dev) ou OTLP (prod).
"""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

logger = logging.getLogger(__name__)


def setup_telemetry(
    service_name: str = "portfolio",
    otlp_endpoint: Optional[str] = None,
    enable_console_export: bool = True,
) -> trace.Tracer:
    """
    Configura OpenTelemetry para a aplicação.

    Args:
        service_name: Nome do serviço para identificação
        otlp_endpoint: Endpoint OTLP (ex: "localhost:4317")
        enable_console_export: Se deve exportar para console (dev)

    Returns:
        Tracer configurado para criar spans
    """
    # Resource identifica o serviço
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": "development"
            if enable_console_export
            else "production",
        }
    )

    # Provider de traces
    provider = TracerProvider(resource=resource)

    # Exporters
    if otlp_endpoint:
        # Produção: exporta para OTLP collector
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info(f"OpenTelemetry: OTLP exporter configured to {otlp_endpoint}")

    if enable_console_export:
        # Dev: exporta para console
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(console_exporter))
        logger.info("OpenTelemetry: Console exporter enabled")

    # Registra provider global
    trace.set_tracer_provider(provider)

    return trace.get_tracer(service_name)


def instrument_app(app, engine=None):
    """
    Instrumenta a aplicação FastAPI e dependências.

    Args:
        app: Instância do FastAPI
        engine: SQLAlchemy engine (opcional)
    """
    # FastAPI auto-instrumentation
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry: FastAPI instrumented")

    # HTTPX client instrumentation
    HTTPXClientInstrumentor().instrument()
    logger.info("OpenTelemetry: HTTPX instrumented")

    # SQLAlchemy instrumentation
    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
        logger.info("OpenTelemetry: SQLAlchemy instrumented")


def create_span(name: str, attributes: Optional[dict] = None):
    """
    Cria um span para tracing manual.

    Usage:
        with create_span("process_data", {"user_id": "123"}):
            # código a ser trackeado
            pass
    """
    tracer = trace.get_tracer(__name__)
    return tracer.start_as_current_span(name, attributes=attributes)


def get_current_trace_context() -> dict:
    """
    Retorna contexto do trace atual para correlação.

    Returns:
        Dict com trace_id e span_id ou vazio se não houver span
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        ctx = span.get_span_context()
        return {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
        }
    return {}


def add_span_attributes(attributes: dict):
    """
    Adiciona atributos ao span atual.

    Args:
        attributes: Dict de atributos a adicionar
    """
    span = trace.get_current_span()
    if span:
        for key, value in attributes.items():
            span.set_attribute(key, value)


def record_exception(exception: Exception, attributes: Optional[dict] = None):
    """
    Registra uma exceção no span atual.

    Args:
        exception: Exceção a registrar
        attributes: Atributos adicionais
    """
    span = trace.get_current_span()
    if span:
        span.record_exception(exception, attributes=attributes)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))
