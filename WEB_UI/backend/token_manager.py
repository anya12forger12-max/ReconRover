import time
import json
import hmac
import base64
import hashlib
from typing import Dict, Any, Optional
from .security_policy import SecurityPolicy


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4))


class TokenManager:
    def __init__(self, policy: SecurityPolicy):
        self.policy = policy

    def generate_token(self, username: str, role: str) -> str:
        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": username,
            "role": role,
            "iat": now,
            "exp": now + int(self.policy.session_timeout_seconds),
        }

        message = f"{_b64encode(json.dumps(header, separators=(',', ':')).encode())}." \
                  f"{_b64encode(json.dumps(payload, separators=(',', ':')).encode())}"
        signature = _b64encode(
            hmac.new(self.policy.jwt_secret.encode(), message.encode(), hashlib.sha256).digest()
        )
        return f"{message}.{signature}"

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split(".")
            if len(parts) != 3 or not all(parts):
                return None

            message = f"{parts[0]}.{parts[1]}"
            expected = _b64encode(
                hmac.new(self.policy.jwt_secret.encode(), message.encode(), hashlib.sha256).digest()
            )
            # Compare in constant time and require the exact algorithm we sign with.
            if not hmac.compare_digest(expected, parts[2]):
                return None

            header = json.loads(_b64decode(parts[0]))
            if header.get("alg") != "HS256" or header.get("typ") != "JWT":
                return None

            payload = json.loads(_b64decode(parts[1]))
            if not isinstance(payload, dict):
                return None
            if time.time() > payload.get("exp", 0):
                return None
            if not isinstance(payload.get("sub"), str) or not isinstance(payload.get("role"), str):
                return None

            return payload
        except Exception:
            return None
