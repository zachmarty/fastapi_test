import os
from pathlib import Path
from fastapi_users.authentication import (
    CookieTransport,
    JWTStrategy,
    AuthenticationBackend,
)
from dotenv import load_dotenv

"""
Подключение стандартной jwt авторизации
"""

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
cookie_transport = CookieTransport(cookie_name="jwt", cookie_max_age=3600)

SECRET = os.getenv("JWT_SECRET")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt", transport=cookie_transport, get_strategy=get_jwt_strategy
)
