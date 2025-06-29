import hashlib
import hmac
import urllib.parse


def validate_telegram_init_data(init_data: str, bot_token: str) -> bool:
    parsed_data = urllib.parse.parse_qs(init_data, keep_blank_values=True)
    parsed_data = {k: v[0] for k, v in parsed_data.items()}

    received_hash = parsed_data.pop("hash", "")
    
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items())
    )

    secret_key = hmac.new(
        key=bot_token.encode(),
        msg=b"WebAppData",
        digestmod=hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(calculated_hash, received_hash)
