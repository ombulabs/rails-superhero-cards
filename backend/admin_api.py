"""Admin API endpoints for managing prompt configurations."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator

from .db import get_session
from .logging_config import logger
from .models import PromptConfig
from .prompt_config_service import invalidate_prompt_config_cache

router = APIRouter(prefix="/admin", tags=["admin"])


# Pydantic models for request/response
class PromptConfigUpdate(BaseModel):
    """Schema for updating a prompt config."""

    validation_prompt: str | None = None
    image_prompt: str | None = None
    themes: list[str] | None = None
    holiday_main_theme: str | None = None

    @field_validator("themes")
    @classmethod
    def validate_themes(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            if not v:
                raise ValueError("At least one theme is required")
            return [theme.strip() for theme in v if theme.strip()]
        return v


class PromptConfigResponse(BaseModel):
    """Schema for prompt config response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    validation_prompt: str
    image_prompt: str
    themes: list[str]
    holiday_main_theme: str


# TODO: Add proper authentication/authorization middleware

@router.get("/prompt-config", response_model=PromptConfigResponse)
async def get_prompt_config() -> PromptConfigResponse:
    """Get the prompt configuration."""
    try:
        with get_session() as session:
            config = session.query(PromptConfig).first()

            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Prompt config not found. Run seed first.",
                )

            # Access all attributes while session is open to avoid DetachedInstanceError
            response_data = PromptConfigResponse(
                id=config.id,
                validation_prompt=config.validation_prompt,
                image_prompt=config.image_prompt,
                themes=config.themes,
                holiday_main_theme=config.holiday_main_theme,
            )
            logger.debug(f"Retrieved config: {config.id}, themes type: {type(config.themes)}")
            return response_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving prompt config: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving config: {str(e)}",
        )

@router.put("/prompt-config", response_model=PromptConfigResponse)
async def update_prompt_config(
    config_data: PromptConfigUpdate,
) -> PromptConfigResponse:
    """Update the prompt configuration."""
    try:
        with get_session() as session:
            config = session.query(PromptConfig).first()

            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Prompt config not found",
                )

            # Update only provided fields
            if config_data.validation_prompt is not None:
                config.validation_prompt = config_data.validation_prompt
            if config_data.image_prompt is not None:
                config.image_prompt = config_data.image_prompt
            if config_data.themes is not None:
                config.themes = config_data.themes
            if config_data.holiday_main_theme is not None:
                config.holiday_main_theme = config_data.holiday_main_theme

            session.commit()
            session.refresh(config)

            # Access all attributes while session is open to avoid DetachedInstanceError
            response_data = PromptConfigResponse(
                id=config.id,
                validation_prompt=config.validation_prompt,
                image_prompt=config.image_prompt,
                themes=config.themes,
                holiday_main_theme=config.holiday_main_theme,
            )

            logger.info("Updated prompt config")

        # Invalidate cache after session is closed
        invalidate_prompt_config_cache()

        return response_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prompt config: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating config: {str(e)}",
        )

# TODO: add post endpoint to create new prompt
# TODO: add list of prompts endpoint
#  TODO: add activate prompts