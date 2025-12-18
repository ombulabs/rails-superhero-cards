"""App dependencies for easy injection."""

import ssl
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import redis.asyncio as redis
from celery import Celery
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from redis import Redis

from .config import settings

broker_use_ssl = {}
redis_backend_use_ssl = {}

use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE} if settings.redis_url.startswith("rediss") else {}

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    task_track_started=True,
    broker_use_ssl=use_ssl,
    redis_backend_use_ssl=use_ssl,
)

celery_app.conf.result_extended = True
celery_app.autodiscover_tasks(["backend.tasks"])
celery_app.conf.result_expires = 300


def get_redis_pubsub_client() -> Redis:
    url = urlparse(settings.redis_url)
    return Redis(
        host=url.hostname,
        port=url.port,
        password=url.password,
        ssl=(url.scheme == "rediss"),
        ssl_cert_reqs=ssl.CERT_NONE if url.scheme == "rediss" else None,
        decode_responses=True,
    )


@asynccontextmanager
async def lifespan(_: FastAPI) -> None:
    """Lifespan context manager initialising the rate limiter.

    Define the context manager to be passed to the FastAPI app object so rate limiting can be applied.
    """
    url = urlparse(settings.redis_url)
    redis_connection = redis.Redis(
        host=url.hostname,
        port=url.port,
        password=url.password,
        ssl=(url.scheme == "rediss"),
        ssl_cert_reqs="none",
    )
    await FastAPILimiter.init(redis_connection)

    yield
    await FastAPILimiter.close()
