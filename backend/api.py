import re

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from .aws_service import S3Service
from .config import settings
from .db import get_session
from .dependencies import celery_app
from .enums import TaskStatus
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

    celery_task = generate_superhero_card.delay(
        image_data=compressed_image_data,
        text=text,
        session_id=session_id,
        holiday_theme=holiday_theme,
    )

    return JSONResponse(
        status_code=202,
        content={
            "task_id": celery_task.id,
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


@router.get("/status/{task_id}")
def check_task_status(task_id: str) -> JSONResponse:
    result = AsyncResult(task_id.strip(), app=celery_app)
    status = TaskStatus(result.status)

    image_base64 = None
    session_id = None
    error_message = None

    if status == TaskStatus.SUCCESS and result.result and (session_id := result.result.get("session_id")):
        error_message = _get_error_from_db(session_id)
        if not error_message:
            image_base64 = _get_card_from_s3(session_id)
            logger.debug(f"Task {task_id} completed successfully for session {session_id}")

    status_description = error_message if error_message else status.description

    return JSONResponse(
        content={
            "status": "error" if error_message else status.status,
            "status_description": status_description,
            "image_base64": image_base64,
            "session_id": session_id,
        }
    )
