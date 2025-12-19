import base64
import os
from io import BytesIO

from llama_index.core.prompts import PromptTemplate
from PIL import Image, ImageDraw, ImageFont
from pillow_heif import register_heif_opener
from pydantic import BaseModel, Field

from .config import settings
from .exceptions import ImageFormatError
from .llms import llm
from .logging_config import log_memory_usage, logger

register_heif_opener()


class ValidationOutput(BaseModel):
    is_valid: bool = Field(..., description="Whether the input is valid and appropriate")
    reason: str = Field(..., description="Brief explanation of why it's valid or invalid")


def validate_image_format(image_data: bytes) -> None:
    try:
        logger.debug(f"Validating image data of size: {len(image_data)} bytes")

        if not image_data:
            raise ImageFormatError("Image data is empty")

        image_buffer = BytesIO(image_data)
        image_buffer.seek(0)

        with Image.open(image_buffer) as image:
            image_format = image.format
            image.verify()
            logger.debug(f"Image format validated: {image_format}")
    except ImageFormatError:
        raise
    except Exception as error:
        logger.error(f"Failed to validate image format: {error}")
        raise ImageFormatError("Unable to process image. Please upload a valid image file (PNG, JPG, HEIC, WebP, etc.)")


def compress_image(image_data: bytes, max_size_bytes: int = 1024 * 1024) -> bytes:
    log_memory_usage("Before image compression")
    with Image.open(BytesIO(image_data)) as image:
        original_size = image.size

        if image.mode != "RGB":
            image = image.convert("RGB")

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=False)  # Skip optimize for speed

        if buffer.tell() <= max_size_bytes:
            logger.info(
                f"Image compressed to {buffer.tell() / 1024:.0f} KB (original: {len(image_data) / 1024:.0f} KB)"
            )
            return buffer.getvalue()

        size_ratio = buffer.tell() / max_size_bytes
        target_scale = min(0.9, 1.0 / (size_ratio**0.5))

        if target_scale < 0.95:
            new_size = (int(original_size[0] * target_scale), int(original_size[1] * target_scale))
            with image.resize(new_size, Image.Resampling.BILINEAR) as resized:
                buffer = BytesIO()
                resized.save(buffer, format="JPEG", quality=85, optimize=False)

                if buffer.tell() <= max_size_bytes:
                    logger.info(
                        f"Resized from {original_size} to {new_size}, "
                        f"compressed to {buffer.tell() / 1024:.0f} KB (original: {len(image_data) / 1024:.0f} KB)"
                    )
                    return buffer.getvalue()

        for quality in [75, 65]:
            buffer = BytesIO()
            if target_scale < 0.95:
                with image.resize(new_size, Image.Resampling.BILINEAR) as resized:
                    resized.save(buffer, format="JPEG", quality=quality, optimize=False)
            else:
                image.save(buffer, format="JPEG", quality=quality, optimize=False)

            if buffer.tell() <= max_size_bytes:
                logger.info(f"Compressed to {buffer.tell() / 1024:.0f} KB with quality={quality}")
                log_memory_usage("After image compression")
                return buffer.getvalue()

        logger.warning(f"Could not compress below {max_size_bytes / 1024:.0f} KB, returning best effort")
        log_memory_usage("After image compression")
        return buffer.getvalue()


async def validate_input(query: str, prompt: PromptTemplate) -> bool:
    logger.debug(f"Validating input: {query[:100]}...")
    validation_result = await llm.astructured_predict(
        output_cls=ValidationOutput,
        prompt=prompt,
        query=query,
    )

    logger.debug(f"Validation result: {validation_result.is_valid} - {validation_result.reason}")

    return validation_result.is_valid


def create_card(image_base64: str, text: str) -> str:
    log_memory_usage("Before card creation")
    image_data = base64.b64decode(image_base64)

    with Image.open(BytesIO(image_data)) as generated_image:
        card_width = generated_image.width + (2 * settings.card_border_size)
        card_height = (
            generated_image.height
            + (2 * settings.card_border_size)
            + settings.card_title_area_height
            + settings.card_branding_area_height
        )

        with Image.new("RGB", (card_width, card_height), "white") as card:
            img_x = settings.card_border_size
            img_y = settings.card_border_size + settings.card_branding_area_height
            card.paste(generated_image, (img_x, img_y))

            draw = ImageDraw.Draw(card)

            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(current_dir, "fonts", "Pacifico-Regular.ttf")

            try:
                font = ImageFont.truetype(font_path, settings.card_font_size)
            except Exception as e:
                logger.warning(f"Warning: Could not load Pacifico font from {font_path}: {e}")
                logger.warning("Falling back to default font")
                font = ImageFont.load_default(size=settings.card_font_size)

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            text_x = (card_width - text_width) // 2

            title_area_start = card_height - settings.card_border_size - settings.card_title_area_height
            title_y = title_area_start + (settings.card_title_area_height - text_height) // 2

            draw.text((text_x, title_y), text, fill="#000000", font=font)

            logo_path = os.path.join(current_dir, "assets", "fastruby-logo.png")
            try:
                with Image.open(logo_path) as logo:
                    aspect_ratio = logo.width / logo.height
                    new_logo_width = int(settings.card_branding_logo_height * aspect_ratio)
                    with logo.resize(
                        (new_logo_width, settings.card_branding_logo_height), Image.Resampling.BILINEAR
                    ) as resized_logo:
                        if resized_logo.mode != "RGBA":
                            resized_logo = resized_logo.convert("RGBA")
                        logo_data = resized_logo.getdata()
                        new_logo_data = []
                        for item in logo_data:
                            new_logo_data.append((item[0], item[1], item[2], int(item[3] * 0.5)))
                        resized_logo.putdata(new_logo_data)

                        branding_area_start = settings.card_border_size

                        logo_x = (card_width - new_logo_width) // 2
                        logo_y = branding_area_start + settings.card_branding_padding_top

                        card.paste(resized_logo, (logo_x, logo_y), resized_logo)

            except Exception as e:
                logger.warning(f"Could not add branding to card: {e}")

            buffer = BytesIO()
            card.save(buffer, format="PNG")
            log_memory_usage("After card creation")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
