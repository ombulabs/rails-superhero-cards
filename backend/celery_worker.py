"""Celery app entry point for the worker."""

import sentry_sdk
from langfuse import Langfuse
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

from .config import settings
from .dependencies import celery_app  # noqa: F401
from .exceptions import ImageFormatError, ImageSizeError, InputValidationError

if settings.environment == "production":
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        enable_tracing=settings.sentry_enable_tracing,
        ignore_errors=[InputValidationError, ImageFormatError, ImageSizeError],
    )

if settings.enable_langfuse:
    langfuse = Langfuse(
        host=settings.langfuse_base_url,
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
    )
    LlamaIndexInstrumentor().instrument()
