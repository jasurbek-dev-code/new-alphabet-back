from typing import List, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import TranslationHistory
from services.transliteration import transliterate_text


class TranslationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def translate_and_record(
        self, user_id: int, original_text: str
    ) -> TranslationHistory:
        """
        Transliterates the text and persists the record into TranslationHistory.
        """
        translated_text = transliterate_text(original_text)

        history_record = TranslationHistory(
            user_id=user_id,
            original_text=original_text,
            translated_text=translated_text,
        )
        self.db.add(history_record)
        await self.db.commit()
        await self.db.refresh(history_record)
        return history_record

    async def get_user_history(
        self, user_id: int, page: int = 1, per_page: int = 20
    ) -> Tuple[List[TranslationHistory], int]:
        """
        Retrieves paginated translation history for a specific user.
        """
        offset = (page - 1) * per_page

        # Total count query
        count_stmt = (
            select(func.count())
            .select_from(TranslationHistory)
            .where(TranslationHistory.user_id == user_id)
        )
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # Items query ordered descending by created_at
        stmt = (
            select(TranslationHistory)
            .where(TranslationHistory.user_id == user_id)
            .order_by(TranslationHistory.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        items_result = await self.db.execute(stmt)
        items = list(items_result.scalars().all())

        return items, total

    async def delete_user_history_item(self, user_id: int, history_id: int) -> bool:
        """
        Deletes a specific history record belonging to the user.
        Returns True if found and deleted, False otherwise.
        """
        stmt = (
            select(TranslationHistory)
            .where(
                TranslationHistory.id == history_id,
                TranslationHistory.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        record = result.scalar_one_or_none()
        if not record:
            return False

        await self.db.delete(record)
        await self.db.commit()
        return True
