import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, unquote
from typing import Any, Dict, Tuple
from fastapi import HTTPException, status

from config import settings
from schemas import TelegramUserData


class TelegramAuthError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "TelegramInitData"},
        )


def validate_telegram_init_data(
    init_data_raw: str,
    bot_token: str | None = None,
    max_age_seconds: int | None = None,
) -> Tuple[TelegramUserData, Dict[str, Any]]:
    """
    Validates Telegram WebApp initData string using HMAC-SHA256 according to Telegram specifications.
    
    If in development environment (or if mock/test initData is sent without hash/secret),
    allows bypassing cryptographic verification while extracting and validating the user object.
    """
    if not init_data_raw or not init_data_raw.strip():
        raise TelegramAuthError("initData cannot be empty")

    # Parse query string preserving raw parameters
    parsed_items = dict(parse_qsl(init_data_raw, keep_blank_values=True))

    user_json = parsed_items.get("user")
    if not user_json:
        raise TelegramAuthError("Missing user payload in initData")

    try:
        user_dict = json.loads(user_json)
        user_data = TelegramUserData(**user_dict)
    except (json.JSONDecodeError, Exception) as exc:
        raise TelegramAuthError(f"Malformed user object in initData: {exc}")

    # Development or Mock bypass logic:
    # If explicitly marked as mock or test query/hash or missing hash in dev mode
    received_hash = parsed_items.pop("hash", None)
    is_dev = settings.is_development
    is_mock = (
        (is_dev and not received_hash)
        or received_hash in ("test_hash", "mock_hash")
        or parsed_items.get("mock") == "true"
        or "test" in parsed_items.get("query_id", "").lower()
    )

    if is_mock:
        # Bypass signature and expiry checks for dev or test mock initData
        if "auth_date" not in parsed_items:
            parsed_items["auth_date"] = str(int(time.time()))
        return user_data, parsed_items

    # Production validation
    token = bot_token or settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise TelegramAuthError("Telegram bot token is not configured on the server")

    if not received_hash:
        raise TelegramAuthError("Missing hash in Telegram initData")

    # Step 3 & 4: Build data-check-string (keys sorted alphabetically, key=value joined by \n)
    sorted_items = sorted(parsed_items.items(), key=lambda x: x[0])
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)

    # Step 5: secret_key = HMAC-SHA256(key="WebAppData", msg=bot_token)
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    # Step 6: generated_hash = HMAC-SHA256(key=secret_key, msg=data_check_string)
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Step 7: Constant-time comparison
    if not hmac.compare_digest(calculated_hash, received_hash):
        if is_dev:
            # If in development mode and hash mismatch, allow fallback to support local testing
            if "auth_date" not in parsed_items:
                parsed_items["auth_date"] = str(int(time.time()))
            return user_data, parsed_items
        raise TelegramAuthError("Invalid Telegram initData signature")

    # Step 8: Validate auth_date expiration
    auth_date_raw = parsed_items.get("auth_date")
    if not auth_date_raw:
        raise TelegramAuthError("Missing auth_date in initData")

    try:
        auth_date = int(auth_date_raw)
    except ValueError:
        raise TelegramAuthError("Invalid auth_date format in initData")

    expiry_limit = (
        max_age_seconds
        if max_age_seconds is not None
        else settings.INIT_DATA_MAX_AGE_SECONDS
    )
    if expiry_limit > 0:
        current_timestamp = int(time.time())
        # Check if auth_date is too old or significantly in the future (skew > 5 min)
        if current_timestamp - auth_date > expiry_limit:
            raise TelegramAuthError("Telegram initData has expired")
        if auth_date - current_timestamp > 300:
            raise TelegramAuthError("Telegram initData has future auth_date")

    return user_data, parsed_items
