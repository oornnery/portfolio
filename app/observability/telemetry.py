from collections.abc import Mapping

from opentelemetry import trace


def add_current_span_event(
    name: str,
    attributes: Mapping[str, str | int | float | bool] | None = None,
) -> None:
    span = trace.get_current_span()
    if not span.is_recording():
        return
    span.add_event(name, attributes=dict(attributes or {}))


def set_current_span_attributes(
    attributes: Mapping[str, str | int | float | bool],
) -> None:
    span = trace.get_current_span()
    if not span.is_recording():
        return
    span.set_attributes(dict(attributes))
