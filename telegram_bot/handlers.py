import os
from pathlib import Path
from aiogram.filters import Command
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from fastapi_auth.schemas import UserCreate, UserRead
from telegram_bot.states import Register, Login
import re
import requests
from fastapi_server.router import *
from main import fastapi_users

reg_router = fastapi_users.get_register_router(UserRead, UserCreate)
log_router = fastapi_users.get_auth_router(auth_backend)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
SITE_URL = os.getenv("SITE_URL")
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
HELP_COMMAND = f"Hi!\nList of awailable commands:\n/register for registration\n\
/login for login\n/logout for logout\n/get_all to get all notes\n/get_one to get one by id\n\
/add_one to add one note\n/fix_one to change note by its id\n/delete to delete note by id\n\
/find_tags to find notes by tags"
cookie_jwt = ''
message_router = Router()

@message_router.message(Command(commands=["help", "start"]))
async def handle_start(message: types.Message):
    await message.answer(text=HELP_COMMAND)


@message_router.message(Command("register"))
async def register(message: types.Message, state: FSMContext):
    await state.set_state(Register.email)
    await message.answer(text="Enter your email.")


@message_router.message(Register.email)
async def register_pass(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    if not re.match(EMAIL_REGEX, message.text):
        await message.answer("Wrong email. Try again.")
    else:
        await state.set_state(Register.password)
        await message.answer(text="Enter your пароль.")


@message_router.message(Register.password)
async def register_finish(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await message.answer(text=SITE_URL)
    link = SITE_URL + "/auth/register"
    await message.answer(text=link)
    try:
        r = requests.post(link)
        await message.answer(
            f"Registration completed.\nYour data is {data['email']} {data['password']}.\nNow you can login /login."
        )
    except requests.exceptions.ConnectionError as e: 
        await message.answer(text="Something went wrong.")
        await message.answer(text=f"{link}\n{str(e)}")
    await state.clear()


@message_router.message(Command("login"))
async def login(message: types.Message, state: FSMContext):
    await state.set_state(Login.email)
    await message.answer(text="Enter your email.")


@message_router.message(Login.email)
async def login_password(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    if not re.match(EMAIL_REGEX, message.text):
        await message.answer("Wrong email. Try again.")
    else:
        await state.set_state(Register.password)
        await message.answer(text="Enter your пароль.")


@message_router.message(Login.password)
async def login_finish(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await message.answer(
        f"Login completed.\nYour data is {data['email']} {data['password']}.\nNow you can login /login."
    )
    await state.clear()


@message_router.message()
async def echo(message: types.Message):
    await message.answer(text="Unkown command. To get commands type /help.")
