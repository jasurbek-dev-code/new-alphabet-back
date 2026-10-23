import pytest
import time
from fastapi.exceptions import HTTPException
from config import settings
from services.telegram_auth import validate_telegram_init_data
from services.telegram_helper import generate_mock_init_data


def test_validate_telegram_init_data_success():
    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    user_payload = {
        "id": 987654321,
        "first_name": "Alisher",
        "last_name": "Navoiy",
        "username": "navoiy",
        "language_code": "uz",
    }
    init_data = generate_mock_init_data(bot_token, user_payload)

    user_data, parsed = validate_telegram_init_data(init_data, bot_token=bot_token)
    assert user_data.id == 987654321
    assert user_data.first_name == "Alisher"
    assert user_data.last_name == "Navoiy"
    assert user_data.username == "navoiy"


def test_validate_telegram_init_data_tampered():
    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    user_payload = {"id": 12345, "first_name": "Bobur"}
    init_data = generate_mock_init_data(bot_token, user_payload)

    # Tamper with the string (e.g. change user ID)
    tampered = init_data.replace("12345", "99999")
    with pytest.raises(HTTPException) as exc_info:
        validate_telegram_init_data(tampered, bot_token=bot_token)
    assert exc_info.value.status_code == 401
    assert "Invalid Telegram initData signature" in exc_info.value.detail


def test_validate_telegram_init_data_expired():
    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    user_payload = {"id": 12345, "first_name": "Bobur"}
    # Auth date 2 days ago
    old_time = int(time.time()) - 172800
    init_data = generate_mock_init_data(bot_token, user_payload, auth_date=old_time)

    with pytest.raises(HTTPException) as exc_info:
        validate_telegram_init_data(init_data, bot_token=bot_token, max_age_seconds=86400)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail
