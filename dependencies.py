from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from schemas import TelegramUserData
from services.telegram_auth import validate_telegram_init_data
from services.user_service import UserService


async def get_current_user(
    authorization: str = Header(
        ...,
        description="Telegram initData query string or 'Bearer <initData>'",
    ),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency to extract and validate the Telegram user from the Authorization header.
    Automatically registers or updates user state if necessary.
    """
    raw_init_data = authorization.strip()
    if raw_init_data.lower().startswith("bearer "):
        raw_init_data = raw_init_data[7:].strip()

    if not raw_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header containing Telegram initData is required",
        )

    user_data, _ = validate_telegram_init_data(raw_init_data)

    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(user_data.id)
    if not user:
        user, _ = await user_service.sync_telegram_user(user_data)

    return user
