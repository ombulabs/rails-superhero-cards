from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, Enum, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CardTheme(StrEnum):
    SUPERHERO = "superhero"
    HOLIDAY = "holiday"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    deactivated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())


class PromptConfig(Base):
    """Stores configurable prompts and themes for card generation."""

    __tablename__ = "prompt_configs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    validation_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    image_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    themes: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    holiday_main_theme: Mapped[str] = mapped_column(Text, nullable=False, default="Hero")
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    theme: Mapped[CardTheme] = Column(Enum(CardTheme), nullable=False)
    aws_object_key: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
