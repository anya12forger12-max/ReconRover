import os
import secrets


class SecurityPolicy:
    def __init__(self):
        self.max_failed_attempts = 5
        self.lockout_duration_seconds = 300 # 5 minutes
        self.session_timeout_seconds = 3600 # 1 hour
        # A secret baked into the bundle lets anyone mint an admin token.
        # Operators must supply one; without it we use a per-process random
        # secret, so a token cannot survive a restart or be guessed.
        self.jwt_secret = os.environ.get("RECON_ROVER_JWT_SECRET") or secrets.token_hex(32)
        self.password_min_length = 8
