import os
from pathlib import Path
from aiogram.filters import Command
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from fastapi_auth.schemas import UserCreate, UserRead
import re
import requests
from fastapi_server.router import *
from fastapi_server.schemas import TagAdd
from main import fastapi_users
from redis.asyncio import Redis
from aiogram.fsm.state import StatesGroup, State

"""Файл для работы с коммандами телеграм бота"""


"""
Состояния для реализации машин состояний
"""


class Register(StatesGroup):
    email = State()
    password = State()


class Login(StatesGroup):
    email = State()
    password = State()


class CreateNote(StatesGroup):
    name = State()
    content = State()
    tags = State()


class SearchNote(StatesGroup):
    tags = State()


redis = Redis()
message_router = Router()
reg_router = fastapi_users.get_register_router(UserRead, UserCreate)
log_router = fastapi_users.get_auth_router(auth_backend)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
SITE_URL = os.getenv("SITE_URL")
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
HELP_COMMAND = f"Hi!\nList of awailable commands:\n/register for registration\n\
/login for login\n/logout for logout\n/get_all to get all notes\n\
/add_one to add one note\n\
/find_tags to find notes by tags"

"""Ответ на помощь или начало общения"""


@message_router.message(Command(commands=["help", "start"]))
async def handle_start(message: types.Message):
    await message.answer(text=HELP_COMMAND)


"""Ответ на команду регистрации"""


@message_router.message(Command("register"))
async def register(message: types.Message, state: FSMContext):
    await state.set_state(Register.email)
    await message.answer(text="Enter your email.")


"""Получение почты"""


@message_router.message(Register.email)
async def register_pass(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    if not re.match(EMAIL_REGEX, message.text):
        await message.answer("Wrong email. Try again.")
    else:
        await state.set_state(Register.password)
        await message.answer(text="Enter your password.")


"""Получение пароля и завершение регистрации"""


@message_router.message(Register.password)
async def register_finish(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    link = SITE_URL + "/auth/register"
    try:
        r = requests.post(
            link, json={"email": data["email"], "password": data["password"]}
        )
        response = r.json()
        if r.status_code != 201:
            await message.answer(response["detail"][0]["msg"])
        else:
            await message.answer(
                f"Registration completed.\nYour data is {data['email']} {data['password']}.\nNow you can login /login."
            )
    except requests.exceptions.ConnectionError as e:
        await message.answer(text=f"Something went wrong. {str(e)}")
    await state.clear()


"""Ответ на команду логин"""


@message_router.message(Command("login"))
async def login(message: types.Message, state: FSMContext):
    await state.set_state(Login.email)
    await message.answer(text="Enter your email.")


"""Получение почты"""


@message_router.message(Login.email)
async def login_password(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    if not re.match(EMAIL_REGEX, message.text):
        await message.answer("Wrong email. Try again.")
    else:
        await state.set_state(Login.password)
        await message.answer(text="Enter your пароль.")


"""Получение пароля и завершение авторизации"""


@message_router.message(Login.password)
async def login_finish(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    link = SITE_URL + "/auth/jwt/login"
    try:
        session = requests.Session()
        r = session.post(
            link, data={"username": data["email"], "password": data["password"]}
        )
        cookie_jwt = session.cookies.get_dict()["jwt"]
        await redis.set(name=str(message.from_user.id), value=cookie_jwt)
        if r.status_code != 204:
            await message.answer("Login error")
        else:
            await message.answer(f"Login completed.You are now can watch notes.")

    except requests.exceptions.ConnectionError as e:
        await message.answer(text="Something went wrong.")
    await state.clear()


"""Ответ на команду получить все заметки"""


@message_router.message(Command("get_all"))
async def get_all_notes(message: types.Message):
    value = await redis.get(name=str(message.from_user.id))
    value = str(value, encoding="utf-8")
    if not value:
        await message.answer("You are not authorized")
        return
    link = SITE_URL + "/notes"
    cookie = {"jwt": value}
    r = requests.get(link, cookies=cookie)
    await message.answer(r.text)


"""Ответ на команду создать одну заметку"""


@message_router.message(Command("add_one"))
async def add_one_note(message: types.Message, state: FSMContext):
    await state.set_state(CreateNote.name)
    await message.answer(text="Enter note title.")


"""Получение наименования"""


@message_router.message(CreateNote.name)
async def add_one_note_text(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateNote.content)
    await message.answer(text="Enter title content.")


"""Получение содержимого"""


@message_router.message(CreateNote.content)
async def add_one_note_tags(message: types.Message, state: FSMContext):
    await state.update_data(content=message.text)
    await state.set_state(CreateNote.tags)
    value = bytes([])
    await redis.set(name=str(message.from_user.id) + "tags", value=value)
    await message.answer(text="Enter each tag by a single message. To stop type ready.")


"""Получение тегов и завершение создания заметки"""


@message_router.message(CreateNote.tags)
async def add_one_note_end(message: types.Message, state: FSMContext):
    if message.text != "ready":
        new_tag = message.text
        data = await state.get_data()
        if "tags" not in data.keys():
            data = [new_tag]
        else:
            old_tags = data["tags"]
            data = old_tags + [new_tag]
        await state.update_data(tags=data)
        await message.answer(text=f"Tag {message.text} added")
    else:

        value = await redis.get(name=str(message.from_user.id))
        value = str(value, encoding="utf-8")
        data = await state.get_data()
        new_tags = []
        for tag in data["tags"]:
            tmp = TagAdd(name=tag)
            new_tags.append(tmp)
        new_note = NoteAdd(name=data["name"], content=data["content"], tags=new_tags)
        link = SITE_URL + "/notes"
        r = requests.post(link, data=new_note.json(), cookies={"jwt": value})
        if r.status_code != 200:
            await message.answer("Validation error, or you are not authorized.")
        else:
            await message.answer(r.text)
        await state.clear()


"""Ответ на команду поиск заметок по тегам"""


@message_router.message(Command("find_tags"))
async def find_tags(message: types.Message, state: FSMContext):
    await state.set_state(SearchNote.tags)
    await message.answer(text="Enter each tag by a single message. To stop type ready.")


"""Получение тегов и завершение поиска"""


@message_router.message(SearchNote.tags)
async def find_tags_end(message: types.Message, state: FSMContext):
    text = message.text
    if text != "ready":
        new_tag = message.text
        data = await state.get_data()
        if "tags" not in data.keys():
            data = [new_tag]
        else:
            old_tags = data["tags"]
            data = old_tags + [new_tag]
        await state.update_data(tags=data)
        await message.answer(text=f"Tag {message.text} added")
    else:
        data = await state.get_data()
        search = TagSearch(tags=data["tags"])
        link = SITE_URL + "/notes/search"
        value = await redis.get(name=str(message.from_user.id))
        value = str(value, encoding="utf-8")
        r = requests.post(link, data=search.json(), cookies={"jwt": value})
        if r.status_code != 200:
            await message.answer("Validation error, or you are not authorized.")
        else:
            await message.answer(r.text)
        await state.clear()


"""Ответ на остальные сообщения"""


@message_router.message()
async def echo(message: types.Message):
    await message.answer(text="Unkown command. To get commands type /help.")
