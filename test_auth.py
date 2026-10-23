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

    # Tamper with the string in production environment
    settings.APP_ENV = "production"
    try:
        tampered = init_data.replace("12345", "99999")
        with pytest.raises(HTTPException) as exc_info:
            validate_telegram_init_data(tampered, bot_token=bot_token)
        assert exc_info.value.status_code == 401
        assert "Invalid Telegram initData signature" in exc_info.value.detail
    finally:
        settings.APP_ENV = "development"


def test_validate_telegram_init_data_dev_mock():
    # Dev mock initData without signature
    dev_init_data = "query_id=test_query&user=%7B%22id%22%3A12345%2C%22first_name%22%3A%22TestUser%22%7D&mock=true"
    user_data, _ = validate_telegram_init_data(dev_init_data)
    assert user_data.id == 12345
    assert user_data.first_name == "TestUser"


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
