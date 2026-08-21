from __future__ import annotations

import os
from importlib import import_module
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)


def configure_tracing(console: bool = False) -> None:
    """Configure local tracing explicitly; disabled by default for offline CI."""
    if os.getenv("OTEL_SDK_DISABLED", "true").lower() == "true":
        return
    provider = TracerProvider()
    if console:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    elif endpoint := os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        module = import_module("opentelemetry.exporter.otlp.proto.grpc.trace_exporter")
        exporter_type: Any = module.OTLPSpanExporter
        provider.add_span_processor(BatchSpanProcessor(exporter_type(endpoint=endpoint)))
    trace.set_tracer_provider(provider)
