from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Column, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CardTheme(StrEnum):
    SUPERHERO = "superhero"
    HOLIDAY = "holiday"


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
