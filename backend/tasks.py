import asyncio
import json

import sentry_sdk

from .card_generator import CardGenerator
from .db import get_session
from .dependencies import celery_app, get_redis_pubsub_client
from .exceptions import ImageFormatError, ImageSizeError, InputValidationError
from .logging_config import log_memory_usage, logger
from .models import Card, CardTheme


def _publish_error_to_stream(session_id: str, error_message: str) -> None:
    try:
        redis_client = get_redis_pubsub_client()
        channel = f"image_stream:{session_id}"
        redis_client.publish(
            channel,
            json.dumps({"type": "error", "message": error_message}),
        )
        redis_client.close()
        logger.debug(f"Published error to SSE stream for session {session_id}")
    except Exception as redis_error:
        logger.error(f"Failed to publish error to Redis: {redis_error}")


def _save_error_to_db(
    session_id: str, text: str, error_message: str, error_type: str, holiday_theme: bool = False
) -> None:
    try:
        with get_session() as db_session:
            card = Card(
                session_id=session_id,
                text=text,
                status="error",
                error_message=error_message,
                theme=CardTheme.HOLIDAY if holiday_theme else CardTheme.SUPERHERO,
            )
            db_session.add(card)
            db_session.commit()
            logger.debug(f"Saved {error_type} error to DB for session {session_id}")
    except Exception as db_error:
        logger.error(f"Failed to save {error_type} error to DB: {db_error}")


@celery_app.task(name="generate_superhero_card")
def generate_superhero_card(session_id: str, text: str, image_data: bytes, holiday_theme: bool = False) -> dict:
    log_memory_usage("Celery task start")
    try:
        asyncio.run(
            CardGenerator(
                image_base64=image_data,
                text=text,
                session_id=session_id,
                holiday_theme=holiday_theme,
            ).generate()
        )
        log_memory_usage("Celery task complete")
    except (InputValidationError, ImageFormatError, ImageSizeError) as error:
        logger.warning(f"User input validation failed for session {session_id}: {type(error).__name__}: {error}")
        error_message = str(error)
        _save_error_to_db(
            session_id=session_id,
            text=text,
            error_message=error_message,
            error_type="validation",
            holiday_theme=holiday_theme,
        )
        _publish_error_to_stream(session_id=session_id, error_message=error_message)
    except Exception as error:
        logger.error(f"Task failed for session {session_id}: {type(error).__name__}: {error}")
        sentry_sdk.capture_exception(error)
        error_message = "Uh oh. Something went wrong... Please try again or contact us."
        _save_error_to_db(
            session_id=session_id,
            text=text,
            error_message=error_message,
            error_type="system",
            holiday_theme=holiday_theme,
        )
        _publish_error_to_stream(session_id=session_id, error_message=error_message)
    return {"session_id": session_id}
