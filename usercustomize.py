from __future__ import annotations

try:
    from app.observability.bootstrap import (
        configure_auto_instrumentation_environment,
        configure_auto_instrumentation_resources,
    )
except Exception:
    configure_auto_instrumentation_environment = None
    configure_auto_instrumentation_resources = None


if configure_auto_instrumentation_environment is not None:
    try:
        configure_auto_instrumentation_environment()
    except Exception:
        pass

if configure_auto_instrumentation_resources is not None:
    try:
        configure_auto_instrumentation_resources()
    except Exception:
        pass
