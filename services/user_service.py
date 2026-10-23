from typing import Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas import TelegramUserData


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def sync_telegram_user(
        self, user_data: TelegramUserData
    ) -> Tuple[User, bool]:
        """
        Synchronizes Telegram user data into the database.
        Registers the user if they don't exist; updates their profile info if they do.
        Returns a tuple of (User, is_new_user).
        """
        user = await self.get_by_telegram_id(user_data.id)
        is_new = False

        if user is None:
            user = User(
                telegram_id=user_data.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                username=user_data.username,
                language_code=user_data.language_code,
            )
            self.db.add(user)
            is_new = True
        else:
            # Update info if changed
            user.first_name = user_data.first_name
            user.last_name = user_data.last_name
            user.username = user_data.username
            user.language_code = user_data.language_code

        await self.db.commit()
        await self.db.refresh(user)
        return user, is_new
