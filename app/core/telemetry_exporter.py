# Telemetry log file exporter for OpenTelemetry.
# Replaces ConsoleSpanExporter to avoid terminal noise.

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Sequence

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


class FileSpanExporter(SpanExporter):
    """
    Exports OpenTelemetry spans to a log file.

    Why: Keeps telemetry data available for debugging without
         cluttering the terminal output during development.

    How: Uses Python's RotatingFileHandler to write spans as JSON,
         with automatic rotation when file gets too large.
    """

    def __init__(
        self,
        log_file: str = "logs/telemetry.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ) -> None:
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create dedicated logger that doesn't propagate to root
        self.logger = logging.getLogger("telemetry.spans")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Don't show in terminal

        # Remove any existing handlers
        self.logger.handlers.clear()

        # Add file handler only
        handler = RotatingFileHandler(
            str(self.log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to log file as JSON."""
        for span in spans:
            span_data = {
                "name": span.name,
                "trace_id": format(span.context.trace_id, "032x"),
                "span_id": format(span.context.span_id, "016x"),
                "parent_id": format(span.parent.span_id, "016x")
                if span.parent
                else None,
                "start_time": span.start_time,
                "end_time": span.end_time,
                "attributes": dict(span.attributes) if span.attributes else {},
                "status": span.status.status_code.name if span.status else None,
            }
            self.logger.info(json.dumps(span_data))

        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        """Cleanup handlers."""
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Flush all handlers."""
        for handler in self.logger.handlers:
            handler.flush()
        return True
