from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.auth import (
    create_access_token,
    get_current_active_user,
    validate_ombulabs_email,
    verify_google_token,
)
from backend.db import get_session
from backend.logging_config import logger
from backend.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


class GoogleLoginRequest(BaseModel):
    google_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    username: str
    deactivated_at: datetime | None

    class Config:
        from_attributes = True

    @property
    def is_active(self) -> bool:
        return self.deactivated_at is None


@router.post("/google", response_model=TokenResponse)
async def google_login(request: GoogleLoginRequest, db: Session = Depends(get_session)) -> TokenResponse:
    google_user_info = verify_google_token(request.google_token)
    email = google_user_info.email
    name = google_user_info.name

    if not validate_ombulabs_email(email):
        logger.warning(f"Access denied for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Login with your @ombulabs.com email.",
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        username = email.split("@")[0]
        user = User(
            name=name,
            username=username,
            email=email,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(email)})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    return current_user
