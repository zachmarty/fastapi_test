import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id : int
    email : str


class UserCreate(schemas.BaseUserCreate):
    pass



class UserUpdate(schemas.BaseUserUpdate):
    pass