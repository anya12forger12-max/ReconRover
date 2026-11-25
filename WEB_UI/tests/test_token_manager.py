import base64
import json
import os
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.security_policy import SecurityPolicy  # noqa: E402
from backend.token_manager import TokenManager  # noqa: E402


class TokenManagerTest(unittest.TestCase):
    def setUp(self):
        os.environ["RECON_ROVER_JWT_SECRET"] = "test-secret-for-unit-tests"
        self.manager = TokenManager(SecurityPolicy())

    def test_valid_token_round_trips(self):
        token = self.manager.generate_token("operator", "admin")
        payload = self.manager.validate_token(token)
        self.assertEqual(payload["sub"], "operator")
        self.assertEqual(payload["role"], "admin")

    def test_static_mock_signature_is_rejected(self):
        now = int(time.time())
        header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
        payload = base64.urlsafe_b64encode(
            json.dumps({"sub": "attacker", "role": "admin", "exp": now + 3600}).encode()
        ).decode().rstrip("=")
        forged = f"{header}.{payload}.mock_signature"
        self.assertIsNone(self.manager.validate_token(forged))

    def test_tampered_payload_is_rejected(self):
        token = self.manager.generate_token("operator", "user")
        head, _, signature = token.split(".")
        payload = base64.urlsafe_b64encode(
            json.dumps({"sub": "operator", "role": "admin", "exp": int(time.time()) + 3600}).encode()
        ).decode().rstrip("=")
        self.assertIsNone(self.manager.validate_token(f"{head}.{payload}.{signature}"))

    def test_expired_token_is_rejected(self):
        policy = SecurityPolicy()
        policy.session_timeout_seconds = -10
        manager = TokenManager(policy)
        self.assertIsNone(manager.validate_token(manager.generate_token("operator", "admin")))


if __name__ == "__main__":
    unittest.main()
