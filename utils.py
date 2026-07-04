import base64
import hashlib
import hmac
import json
import secrets
import string
import time
import random
from flask_mail import Message

secret_key = "tunu-journal-secret"


def gen_id(prefix="ID", length=10, upper=False):
    letters = string.ascii_letters
    if upper:
        letters = letters.upper()
    chars = letters + string.digits
    return prefix + "-" + "".join(secrets.choice(chars) for _ in range(length))


def generate_token(user_id, tkv, expires_in=86400):
    payload = {
        "user_id": user_id,
        "tkv": tkv,
        "exp": int(time.time()) + expires_in
    }

    payload_json = json.dumps(payload, separators=(",", ":"))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()

    signature = hmac.new(
        secret_key.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}::{signature}"


def verify_token(token):
    try:
        payload_b64, signature = token.split("::")

        expected = hmac.new(
            secret_key.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected, signature):
            return None

        payload = json.loads(
            base64.urlsafe_b64decode(payload_b64.encode()).decode()
        )

        if payload["exp"] < time.time():
            return None

        return payload

    except Exception:
        return None


def generate_otp():
    return str(random.randint(100000, 999999))



"""

"""