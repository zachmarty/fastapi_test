from fastapi import FastAPI
from contextlib import asynccontextmanager

import fastapi_users
from fastapi_auth.manager import get_user_manager
from fastapi_auth.models import User, create_db_and_tables, drop_user_db
from fastapi_auth.schemas import UserCreate, UserRead
from fastapi_server.models import create_tables, drop_tables
from fastapi_server.router import router as notes_router
from fastapi_auth.auth import auth_backend


"""
Файл инициализации fastapi приложения
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_tables()
    await create_tables()
    await drop_user_db()
    await create_db_and_tables()
    print("created")
    yield


fastapi_users = fastapi_users.FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(lifespan=lifespan)
app.include_router(notes_router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
