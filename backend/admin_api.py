"""Admin API endpoints for managing prompt configurations."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator

from .db import get_session
from .logging_config import logger
from .models import PromptConfig, PromptConfigType
from .prompt_config_service import (
    DEFAULT_HOLIDAY_IMAGE_PROMPT,
    DEFAULT_HOLIDAY_THEMES,
    DEFAULT_HOLIDAY_VALIDATION_PROMPT,
    invalidate_prompt_config_cache,
)

router = APIRouter(prefix="/admin", tags=["admin"])

# Pydantic models for request/response
class PromptConfigCreate(BaseModel):
    """Schema for creating a prompt config."""

    config_type: PromptConfigType
    validation_prompt: str
    image_prompt: str
    themes: list[str]

    @field_validator("themes")
    @classmethod
    def validate_themes(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one theme is required")
        return [theme.strip() for theme in v if theme.strip()]

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
        return

class PromptConfigResponse(BaseModel):
    """Schema for prompt config response."""

    id: UUID
    config_type: PromptConfigType
    validation_prompt: str
    image_prompt: str
    themes: list[str]

    class Config:
        from_attributes = True

class PromptConfigListResponse(BaseModel):
    """Schema for listing prompt configs."""

    configs: list[PromptConfigResponse]

# TODO: Add proper authentication/authorization middleware

@router.get("/prompt-configs", response_model=PromptConfigListResponse)
async def list_prompt_configs() -> dict[str, Any]:
    """List all prompt configurations."""
    with get_session() as session:
        configs = session.query(PromptConfig).all()
        return {"configs": configs}

@router.post(
    "/prompt-configs",
    response_model=PromptConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prompt_config(
    config_data: PromptConfigCreate,
    # TODO: Add user dependency for auth
    # current_user: User = Depends(get_current_admin_user),
) -> PromptConfig:
    """Create a new prompt configuration."""
    with get_session() as session:
        # Check if config already exists
        existing = (
            session.query(PromptConfig)
            .filter(PromptConfig.config_type == config_data.config_type)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Prompt config for '{config_data.config_type}' already exists. Use PUT to update.",
            )

        config = PromptConfig(
            config_type=config_data.config_type,
            validation_prompt=config_data.validation_prompt,
            image_prompt=config_data.image_prompt,
            themes=config_data.themes,
        )
        session.add(config)
        session.flush()  # Get the ID before commit

        logger.info(f"Created prompt config for '{config_data.config_type}'")
        invalidate_prompt_config_cache()

        return config

@router.put("/prompt-configs/{config_type}", response_model=PromptConfigResponse)
async def update_prompt_config(
    config_type: PromptConfigType,
    config_data: PromptConfigUpdate,
    # TODO: Add user dependency for auth
    # current_user: User = Depends(get_current_admin_user),
) -> PromptConfig:
    """Update an existing prompt configuration."""
    with get_session() as session:
        config = (
            session.query(PromptConfig)
            .filter(PromptConfig.config_type == config_type)
            .first()
        )
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt config for '{config_type}' not found",
            )

        # Update only provided fields
        if config_data.validation_prompt is not None:
            config.validation_prompt = config_data.validation_prompt
        if config_data.image_prompt is not None:
            config.image_prompt = config_data.image_prompt
        if config_data.themes is not None:
            config.themes = config_data.themes


        logger.info(f"Updated prompt config for '{config_type}'")
        invalidate_prompt_config_cache()

        return config
