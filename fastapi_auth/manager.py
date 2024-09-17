import os
from pathlib import Path
from typing import Optional

from fastapi import Depends, Request
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users import BaseUserManager, IntegerIDMixin

from fastapi_auth.models import User, get_user_db
from dotenv import load_dotenv

from fastapi_users import schemas, models

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SECRET = os.getenv("AUTH_SECRET")
"""
Менеджер для работы с пользователями. Здесь немного изменен метод create
для того чтобы поля is_active, is_verified по умолчанию были True
"""


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: User, request: Request | None = None
    ) -> None:
        print(f"User {user.id} has registrated.")

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["is_verified"] = True
        user_dict["is_active"] = True
        user_dict["is_superuser"] = False
        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
