from langfuse import get_client, observe, propagate_attributes

from .aws_service import S3Service
from .config import settings
from .db import get_session
from .logging_config import logger
from .models import Card, CardTheme
from .workflow import ImageGenWorkflow
from .workflow_holiday import HolidayImageGenWorkflow

langfuse = get_client()


class CardGenerator:
    def __init__(
        self,
        image_base64: bytes,
        text: str,
        session_id: str,
        holiday_theme: bool = False,
    ):
        self.image_data = image_base64
        self.text = text
        self.session_id = session_id
        self.holiday_theme = holiday_theme
        self.s3_service = S3Service(
            folder_prefix=settings.s3_holiday_folder_prefix if holiday_theme else settings.s3_folder_prefix
        )

    async def generate(self) -> dict:
        logger.info(f"Generating hero card for session id: {self.session_id}")
        result = await self._run_holiday_workflow() if self.holiday_theme else await self._run_superhero_workflow()
        logger.info(f"Generated hero card for session id: {self.session_id}")

        aws_object_key = self._store_card_in_bucket(result["image_base64"])

        self._save_to_db(
            session_id=self.session_id,
            text=self.text,
            aws_object_key=aws_object_key,
            theme=CardTheme.HOLIDAY if self.holiday_theme else CardTheme.SUPERHERO,
        )

        return {
            "session_id": self.session_id,
        }

    @observe(name="rails_superhero_card_workflow")
    async def _run_superhero_workflow(self) -> dict:
        with propagate_attributes(
            session_id=self.session_id,
        ):
            workflow = ImageGenWorkflow()
            return await workflow.run(image_data=self.image_data, skills=self.text)

    @observe(name="rails_holiday_card_workflow")
    async def _run_holiday_workflow(self) -> dict:
        with propagate_attributes(
            session_id=self.session_id,
        ):
            workflow = HolidayImageGenWorkflow()
            return await workflow.run(image_data=self.image_data, message=self.text)

    def _store_card_in_bucket(self, image_data: str) -> str:
        logger.info("Storing image in AWS")

        try:
            object_key = self.s3_service.upload_image(
                image_base64=image_data,
                session_id=self.session_id,
            )
            logger.info("Image stored successfully!")
        except Exception as error:
            object_key = None
            logger.error(f"Failed to upload to AWS: {error}")

        return object_key

    @staticmethod
    def _save_to_db(
        session_id: str,
        text: str,
        aws_object_key: str,
        theme: CardTheme,
    ) -> None:
        try:
            with get_session() as session:
                card = Card(
                    session_id=session_id,
                    text=text,
                    aws_object_key=aws_object_key,
                    status="complete",
                    theme=theme,
                )
                session.add(card)
                session.commit()
        except Exception as error:
            logger.error(f"Failed to save to DB: {error}")
