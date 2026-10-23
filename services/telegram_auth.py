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
    
    Algorithm:
    1. Parse query string into key-value pairs.
    2. Extract and remove the `hash` parameter.
    3. Sort remaining parameters alphabetically in the format `key=value`.
    4. Join sorted pairs with newline `\\n` to create data_check_string.
    5. Compute secret_key = HMAC_SHA256("WebAppData", bot_token).
    6. Compute generated_hash = HMAC_SHA256(secret_key, data_check_string).hex().
    7. Compare generated_hash with received hash using constant-time comparison.
    8. Check auth_date for expiration (if max_age_seconds > 0).
    """
    token = bot_token or settings.TELEGRAM_BOT_TOKEN
    if not token:
        raise TelegramAuthError("Telegram bot token is not configured on the server")

    if not init_data_raw or not init_data_raw.strip():
        raise TelegramAuthError("initData cannot be empty")

    # Parse query string preserving raw parameters
    parsed_items = dict(parse_qsl(init_data_raw, keep_blank_values=True))

    received_hash = parsed_items.pop("hash", None)
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

    # Parse user JSON object
    user_json = parsed_items.get("user")
    if not user_json:
        raise TelegramAuthError("Missing user payload in initData")

    try:
        user_dict = json.loads(user_json)
        user_data = TelegramUserData(**user_dict)
    except (json.JSONDecodeError, Exception) as exc:
        raise TelegramAuthError(f"Malformed user object in initData: {exc}")

    return user_data, parsed_items
