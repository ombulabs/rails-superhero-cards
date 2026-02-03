"""Service for managing prompt configurations."""

from functools import lru_cache
from typing import Any

from .db import get_session
from .logging_config import logger
from .models import PromptConfig

# Cache version - increment to invalidate cache
_cache_version = 0


def invalidate_prompt_config_cache() -> None:
    """Invalidate the prompt config cache when configs are updated."""
    global _cache_version
    _cache_version += 1
    get_prompt_config.cache_clear()
    logger.info("Prompt config cache invalidated")


@lru_cache(maxsize=10)
def get_prompt_config(cache_version: int = 0) -> dict[str, Any]:  # noqa: ARG001
    """
    Get prompt configuration from database with caching.

    Args:
        cache_version: Used to invalidate cache (not used in function body)

    Returns:
        Dictionary with validation_prompt, image_prompt, and themes

    Raises:
        ValueError: If config not found in database (run seed first)
    """
    with get_session() as session:
        config = session.query(PromptConfig).first()

        if config:
            logger.debug("Loaded prompt config from database")
            return {
                "validation_prompt": config.validation_prompt,
                "image_prompt": config.image_prompt,
                "themes": config.themes,
            }

    raise ValueError("Prompt config not found in database. Run seed first.")


def get_holiday_config() -> dict[str, Any]:
    """Get prompt configuration (kept for backward compatibility)."""
    return get_prompt_config(_cache_version)


def get_superhero_config() -> dict[str, Any]:
    """Get prompt configuration (kept for backward compatibility)."""
    return get_prompt_config(_cache_version)
