import asyncio
import json
import re
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi_limiter.depends import RateLimiter

from .aws_service import S3Service
from .config import settings
from .db import get_session
from .dependencies import get_redis_pubsub_client
from .exceptions import ImageFormatError
from .logging_config import logger
from .models import Card
from .tasks import generate_superhero_card
from .utils import compress_image, validate_image_format

router = APIRouter()


@router.post("/generate-hero-card", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def generate_hero_card(
    text: str = Form(...),
    image: UploadFile = File(...),
    session_id: str = Form(...),
    holiday_theme: bool = Form(False),
) -> JSONResponse:
    image_data = await image.read()

    try:
        validate_image_format(image_data)
    except ImageFormatError as error:
        logger.warning(f"Image format validation failed for session {session_id}: {error}")
        return JSONResponse(status_code=400, content={"error": str(error)})

    try:
        compressed_image_data = compress_image(image_data, max_size_bytes=1024 * 1024)
    except Exception as error:
        logger.error(f"Image compression failed for session {session_id}: {error}")
        return JSONResponse(status_code=500, content={"error": "Failed to process image"})

    text = re.sub(r"\s+", " ", text.strip())

    generate_superhero_card.delay(
        image_data=compressed_image_data,
        text=text,
        session_id=session_id,
        holiday_theme=holiday_theme,
    )

    return JSONResponse(
        status_code=202,
        content={
            "session_id": session_id,
            "message": "Card generation started",
        },
    )


def _get_card_from_s3(session_id: str) -> str | None:
    try:
        with get_session() as db_session:
            card = db_session.query(Card).filter(Card.session_id == session_id).first()
            if not card or not card.aws_object_key:
                logger.warning(f"No card or aws_object_key found for session {session_id}")
                return None

            folder_prefix = settings.s3_holiday_folder_prefix if card.theme == "holiday" else settings.s3_folder_prefix
            s3_service = S3Service(folder_prefix=folder_prefix)

            image_base64 = s3_service.get_image_base64(card.aws_object_key)
            logger.debug(f"Retrieved card from S3 for session {session_id}")
            return image_base64
    except Exception as error:
        logger.error(f"Error getting card from S3 for session {session_id}: {error}")
        return None


def _get_error_from_db(session_id: str) -> str | None:
    try:
        with get_session() as db_session:
            card = db_session.query(Card).filter(Card.session_id == session_id).first()
            if card:
                return card.error_message if card.error_message else None
            logger.warning(f"No card found in DB for session {session_id}")
            return None
    except Exception as error:
        logger.error(f"Error getting error from db session {session_id}: {error}")
        return None


@router.get("/stream/{session_id}")
async def stream_partial_images(session_id: str) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        redis_client = get_redis_pubsub_client()
        pubsub = redis_client.pubsub()
        channel = f"image_stream:{session_id}"

        try:
            pubsub.subscribe(channel)
            logger.info(f"SSE client connected for session {session_id}")

            yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"

            timeout = 300  # 5 minutes max
            start_time = asyncio.get_event_loop().time()

            while True:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    logger.warning(f"SSE timeout for session {session_id}")
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Timeout'})}\n\n"
                    break

                message = pubsub.get_message(timeout=0.1)
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    logger.debug(f"Streaming event to client: {data.get('type')}")
                    yield f"data: {json.dumps(data)}\n\n"

                    if data.get("type") == "complete":
                        break

                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in SSE stream for session {session_id}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Stream error'})}\n\n"
        finally:
            pubsub.unsubscribe(channel)
            pubsub.close()
            redis_client.close()
            logger.info(f"SSE client disconnected for session {session_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
