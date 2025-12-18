from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    environment: Literal["development", "staging", "production"] = "development"
    allow_origins: str | list[str] = []

    @field_validator("allow_origins", mode="before")
    def split_str(cls, v: str | list[str]) -> list[str]:  # noqa: N805
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    database_url: str

    @field_validator("database_url", mode="before")
    def format_postgres_url(cls, v: str) -> str:  # noqa: N805
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    log_level: str = "DEBUG"

    openai_api_key: str
    openai_max_retries: int = 3
    llm_temperature: float = 0.9

    image_gen_model: str = "gpt-image-1"
    default_llm: str = "gpt-4o-mini"

    generated_image_size: str = "1024x1024"
    mock_upload_file_name: str = "uploaded_image.png"

    card_border_size: int = 40
    card_title_area_height: int = 120
    card_font_size: int = 60
    card_branding_area_height: int = 100
    card_branding_logo_height: int = 50
    card_branding_padding_top: int = 15

    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str | None = None
    aws_endpoint_url: str | None = None
    s3_bucket_name: str | None = None
    s3_folder_prefix: str | None = None
    s3_holiday_folder_prefix: str | None = None

    redis_url: str = "redis://localhost:6379/0"

    sentry_dsn: str = ""
    sentry_enable_tracing: bool = False

    enable_langfuse: bool = False
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_base_url: str = ""

    price_per_image: float = 0.04


settings = Settings()
