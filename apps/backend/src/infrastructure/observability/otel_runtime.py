from __future__ import annotations

import logging
from typing import Literal

from fastapi import FastAPI

from src.core.config import settings
from src.core.observability import _parse_otlp_headers

logger = logging.getLogger(__name__)
_OTEL_CONFIGURED = False


def configure_observability_runtime(
    app: FastAPI | None = None,
    runtime: Literal["api", "worker"] = "api",
) -> None:
    global _OTEL_CONFIGURED

    if _OTEL_CONFIGURED:
        return
    if not settings.OBSERVABILITY_ENABLED or not settings.OTEL_ENABLED:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except Exception as error:  # pragma: no cover
        logger.warning("OpenTelemetry initialization skipped: %s", error)
        return

    service_name = settings.OTEL_SERVICE_NAME or settings.PROJECT_NAME
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "hello-wiki",
            "deployment.environment": "dev" if settings.DEBUG else "prod",
            "service.instance.id": runtime,
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        headers=_parse_otlp_headers(settings.OTEL_EXPORTER_OTLP_HEADERS),
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(tracer_provider)

    if app is not None and settings.OTEL_INSTRUMENT_FASTAPI:
        FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

    if settings.OTEL_INSTRUMENT_LLAMAINDEX:
        try:
            from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

            LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
        except Exception as error:  # pragma: no cover
            logger.warning("LlamaIndex OpenInference instrumentation skipped: %s", error)

    _OTEL_CONFIGURED = True
    logger.info(
        "OpenTelemetry configured. endpoint=%s runtime=%s",
        settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        runtime,
    )
