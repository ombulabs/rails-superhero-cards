"""Admin API endpoints for managing prompt configurations."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, field_validator

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

    id: UUID
    validation_prompt: str
    image_prompt: str
    themes: list[str]

    class Config:
        from_attributes = True


# TODO: Add proper authentication/authorization middleware

@router.get("/prompt-config", response_model=PromptConfigResponse)
async def get_prompt_config() -> PromptConfig:
    """Get the prompt configuration."""
    with get_session() as session:
        config = session.query(PromptConfig).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prompt config not found. Run seed first.",
            )

        return config

@router.put("/prompt-config", response_model=PromptConfigResponse)
async def update_prompt_config(
    config_data: PromptConfigUpdate,
) -> PromptConfig:
    """Update the prompt configuration."""
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

        session.commit()
        session.refresh(config)

        logger.info("Updated prompt config")
        invalidate_prompt_config_cache()

        return config
