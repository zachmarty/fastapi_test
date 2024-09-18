from fastapi_users import schemas

"""
Схемы для работы с пользователями
"""


class UserRead(schemas.BaseUser[int]):
    id: int


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
