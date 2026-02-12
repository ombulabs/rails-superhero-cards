import json
import random
from contextlib import nullcontext
from io import BytesIO

from langfuse import get_client
from langfuse.media import LangfuseMedia
from llama_index.core.prompts import PromptTemplate
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

from .config import settings
from .dependencies import get_redis_pubsub_client
from .exceptions import InputValidationError
from .llms import openai_client
from .logging_config import log_memory_usage, logger
from .prompt_config_service import get_holiday_config
from .utils import create_card, validate_input


class ValidatedInputEvent(Event):
    is_valid: bool


class HolidayThemeEvent(Event):
    theme: str


class GeneratedImageEvent(Event):
    image_base64: str
    theme: str


class HolidayImageGenWorkflow(Workflow):
    @step()
    async def validate_input(self, ev: StartEvent, ctx: Context) -> ValidatedInputEvent:
        image_data = ev.get("image_data")
        if not image_data:
            raise ValueError("An uploaded image is required.")

        message = ev.get("message", "")
        session_id = ev.get("session_id")

        config = get_holiday_config()
        await ctx.store.set("image_data", image_data)
        await ctx.store.set("message", message)
        await ctx.store.set("session_id", session_id)

        validation_prompt = PromptTemplate(config["validation_prompt"])
        is_valid = await validate_input(query=message, prompt=validation_prompt)

        if not is_valid:
            raise InputValidationError(
                "Sorry, we cannot generate a card with that message. Please enter an appropriate message"
            )

        return ValidatedInputEvent(is_valid=is_valid)

    @step()
    async def pick_theme(self, ev: ValidatedInputEvent, ctx: Context) -> HolidayThemeEvent:  # noqa: ARG002
        config = get_holiday_config()
        themes = config["themes"]
        theme = random.choice(themes)  # noqa: S311
        logger.debug(f"Holiday theme: {theme}")

        return HolidayThemeEvent(theme=theme)

    @step()
    async def generate_image(self, ev: HolidayThemeEvent, ctx: Context) -> GeneratedImageEvent:
        image_data = await ctx.store.get("image_data")
        session_id = await ctx.store.get("session_id")
        message = await ctx.store.get("message", "")
        config = get_holiday_config()

        image_file = BytesIO(image_data)
        image_file.name = settings.mock_upload_file_name

        prompt = config["image_prompt"].format(theme=ev.theme)

        redis_client = get_redis_pubsub_client()
        channel = f"image_stream:{session_id}"

        if settings.enable_langfuse:
            langfuse = get_client()
            observation_context = langfuse.start_as_current_observation(
                as_type="generation",
                name="openai.images.edit",
                model=settings.image_gen_model,
                input={
                    "prompt": prompt,
                    "size": settings.generated_image_size,
                },
            )
        else:
            observation_context = nullcontext()

        log_memory_usage("Before OpenAI image generation")

        with observation_context as obs:
            stream = openai_client.images.edit(
                image=image_file,
                prompt=prompt,
                model=settings.image_gen_model,
                n=1,
                size=settings.generated_image_size,
                stream=True,
                partial_images=3,
            )

            generated_image_base64 = None
            partial_count = 0

            for event in stream:
                logger.debug(f"Received event type: {event.type} for session {session_id}")

                if event.type == "image_generation.partial_image" or event.type == "image_edit.partial_image":
                    partial_count += 1
                    partial_image_base64 = event.b64_json
                    logger.debug(f"Received partial image {partial_count} for session {session_id}")

                    partial_card_base64 = create_card(image_base64=partial_image_base64, text=message)

                    redis_client.publish(
                        channel,
                        json.dumps(
                            {
                                "type": "partial",
                                "image_base64": partial_card_base64,
                                "partial_index": partial_count,
                            }
                        ),
                    )

                elif event.type == "image_generation.completed" or event.type == "image_edit.completed":
                    generated_image_base64 = event.b64_json
                    logger.debug(f"Received final image for session {session_id}")
                else:
                    logger.warning(f"Unknown event type: {event.type}")

            if settings.enable_langfuse:
                image_media = LangfuseMedia(base64_data_uri=f"data:image/png;base64,{generated_image_base64}")
                total_cost = settings.price_per_image

                obs.update(
                    output={
                        "holiday_theme": ev.theme,
                        "image": image_media,
                    },
                    usage_details={"images": 1},
                    cost_details={"images": float(total_cost)},
                    metadata={
                        "costUsd": total_cost,
                        "generatedImageSize": settings.generated_image_size,
                        "partialImagesReceived": partial_count,
                    },
                )

        redis_client.close()
        log_memory_usage("After OpenAI image generation")
        logger.debug("Holiday card generated.")

        return GeneratedImageEvent(image_base64=generated_image_base64, theme=ev.theme)

    @step()
    async def generate_card(self, ev: GeneratedImageEvent, ctx: Context) -> StopEvent:
        message = await ctx.store.get("message", "")
        session_id = await ctx.store.get("session_id")

        logger.debug(f"Creating holiday card with theme: {ev.theme}")
        final_card_base64 = create_card(image_base64=ev.image_base64, text=message)

        redis_client = get_redis_pubsub_client()
        channel = f"image_stream:{session_id}"
        redis_client.publish(
            channel,
            json.dumps(
                {
                    "type": "complete",
                    "image_base64": final_card_base64,
                }
            ),
        )
        redis_client.close()

        return StopEvent(
            result={
                "image_base64": final_card_base64,
            }
        )
