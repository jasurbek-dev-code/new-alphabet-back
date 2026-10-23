import hashlib
import hmac
import json
import time
from urllib.parse import urlencode


def generate_mock_init_data(
    bot_token: str,
    user_dict: dict,
    auth_date: int | None = None,
    query_id: str = "AAHdF6IQAAAAAN0XohDhrOrc",
) -> str:
    """Helper for testing: generates a valid Telegram initData string signed with bot_token."""
    if auth_date is None:
        auth_date = int(time.time())

    params = {
        "auth_date": str(auth_date),
        "query_id": query_id,
        "user": json.dumps(user_dict, separators=(",", ":")),
    }

    # Sort alphabetically
    sorted_items = sorted(params.items(), key=lambda x: x[0])
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    hash_val = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    params["hash"] = hash_val
    return urlencode(params)
