"""OpenTelemetry tracing using the GenAI semantic conventions (gen_ai.* attributes).

The GenAI conventions are still at "Development" status and now live in the
open-telemetry/semantic-conventions-genai repo, so attribute names are centralised here
to make upgrades a one-file change.

Only the opentelemetry-api is required; without an SDK every span is a no-op.
Install the `otel` extra and set PRIORAUTH_OTEL=console (or otlp) to export.
"""
from __future__ import annotations

import os
from contextlib import contextmanager

try:
    from opentelemetry import trace
except ImportError:  # pragma: no cover - api is optional too
    trace = None

AGENT_NAME = "priorauth-copilot"

# Attribute keys (GenAI semantic conventions).
OPERATION = "gen_ai.operation.name"
PROVIDER = "gen_ai.provider.name"
REQUEST_MODEL = "gen_ai.request.model"
INPUT_TOKENS = "gen_ai.usage.input_tokens"
OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
AGENT = "gen_ai.agent.name"
TOOL = "gen_ai.tool.name"

_configured = False


def configure() -> None:
    global _configured
    mode = os.getenv("PRIORAUTH_OTEL", "").lower()
    if _configured or trace is None or not mode:
        return
    try:
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
    except ImportError:
        print("PRIORAUTH_OTEL is set but opentelemetry-sdk is not installed: pip install '.[otel]'")
        return
    provider = TracerProvider(resource=Resource.create({"service.name": AGENT_NAME}))
    if mode == "otlp":
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    else:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _configured = True


@contextmanager
def span(name: str, **attributes):
    """Start a span; attribute values must already be PHI-free (callers pass redacted data only)."""
    if trace is None:
        yield None
        return
    tracer = trace.get_tracer(AGENT_NAME)
    with tracer.start_as_current_span(name) as s:
        for k, v in attributes.items():
            if v is not None:
                s.set_attribute(k, v)
        yield s
