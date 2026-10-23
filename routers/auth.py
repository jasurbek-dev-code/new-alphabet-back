from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from models import User
from schemas import AuthRequest, AuthResponse, UserResponse
from services.telegram_auth import validate_telegram_init_data
from services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & User Sync"])


@router.post(
    "/sync",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate Telegram initData and synchronize user",
    description="Validates Telegram WebApp initData HMAC-SHA256 signature, registers user if absent, or updates their profile.",
)
async def authenticate_and_sync_user(
    payload: AuthRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    # 1. Validate initData
    user_data, parsed_params = validate_telegram_init_data(payload.init_data)

    # 2. Sync user in DB
    user_service = UserService(db)
    user, is_new = await user_service.sync_telegram_user(user_data)

    auth_timestamp = int(parsed_params.get("auth_date", 0))
    auth_dt = datetime.fromtimestamp(auth_timestamp, tz=timezone.utc)

    return AuthResponse(
        user=UserResponse.model_validate(user),
        is_new_user=is_new,
        auth_date=auth_dt,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user details via Authorization / initData header",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)

