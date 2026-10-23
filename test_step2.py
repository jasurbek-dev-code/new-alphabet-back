import asyncio
import os
import sys

# Ensure current dir is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import AsyncSessionLocal, init_db
from models import User, TranslationHistory
from schemas import TelegramUserData
from services.telegram_auth import validate_telegram_init_data
from services.telegram_helper import generate_mock_init_data
from services.transliteration import transliterate_text
from services.translation_service import TranslationService
from services.user_service import UserService


async def run_integration_tests():
    print("--- 1. Testing database init ---")
    await init_db()

    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    user_payload = {
        "id": 999888777,
        "first_name": "Temur",
        "last_name": "Bek",
        "username": "temurbek",
        "language_code": "uz",
    }
    init_data = generate_mock_init_data(bot_token, user_payload)

    print("--- 2. Testing user sync service ---")
    async with AsyncSessionLocal() as db:
        user_data, _ = validate_telegram_init_data(init_data, bot_token=bot_token)
        user_service = UserService(db)
        user, is_new = await user_service.sync_telegram_user(user_data)
        assert user.telegram_id == 999888777
        print(f"User synced: {user}, is_new: {is_new}")

    print("--- 3. Testing transliteration & translation persistence ---")
    async with AsyncSessionLocal() as db:
        trans_service = TranslationService(db)
        input_text = "Shaxmat chempioni O'zbekistonda g'olib bo'ldi va ma'no berdi."
        record = await trans_service.translate_and_record(user.telegram_id, input_text)
        print("Original:", record.original_text)
        print("Translated (UTF-8 bytes):", record.translated_text.encode("utf-8"))
        assert "Şaxmat" in record.translated_text
        assert "çempioni" in record.translated_text
        assert "Ōzbekistonda" in record.translated_text
        assert "ğolib" in record.translated_text
        assert "bōldi" in record.translated_text
        assert "ma'no" in record.translated_text  # apostrophe preserved

    print("--- 4. Testing translation history pagination ---")
    async with AsyncSessionLocal() as db:
        trans_service = TranslationService(db)
        items, total = await trans_service.get_user_history(user.telegram_id, page=1, per_page=10)
        assert total >= 1
        assert items[0].user_id == 999888777
        print(f"Fetched {len(items)} history items out of {total} total items.")

    print("\n>>> All Step 2 integration tests completed successfully! <<<")


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
