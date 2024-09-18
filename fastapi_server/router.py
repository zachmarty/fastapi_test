from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers

from fastapi_auth.manager import get_user_manager
from fastapi_auth.models import User
from fastapi_server.management import NoteORM
from fastapi_server.schemas import NoteAdd, NoteFix, TagSearch
from fastapi_auth.auth import auth_backend

router = APIRouter(
    prefix="/notes",
    tags=[
        "Notes",
    ],
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_user = fastapi_users.current_user()

"""
Файл для работы с роутами
"""


@router.get("/")
async def get_notes(user: User = Depends(current_user)):
    """
    Роут на получение всех заметки
    """
    notes = await NoteORM.get_all()
    return {"data": notes}


@router.post("/")
async def add_note(note: NoteAdd, user: User = Depends(current_user)):
    """
    Роут на создание заметки
    """
    print(user.id)
    await NoteORM.add_one(note, user.id)
    return "ok"


@router.get("/{id}")
async def get_note(id: int, user: User = Depends(current_user)):
    """
    Роут на получение одной заметки
    """
    result = await NoteORM.get_one(id)
    return result


@router.put("/{id}")
async def update_note(id: int, note: NoteAdd, user: User = Depends(current_user)):
    """
    Роут на обновление заметки через put
    """
    result = await NoteORM.update_one(id, note, user.id)
    return result


@router.patch("/{id}")
async def fix_note(id: int, note: NoteFix, user: User = Depends(current_user)):
    """
    Роут на обновление заметки через patch
    """
    result = await NoteORM.fix_one(id, note, user.id)
    return result


@router.delete("/{id}")
async def delete_one(id: int, user: User = Depends(current_user)):
    """
    Роут на удаление заметки
    """
    result = await NoteORM.delete_one(id, user.id)
    return result


@router.post("/search")
async def tag_search(tags: TagSearch, user: User = Depends(current_user)):
    """
    Роут на поиск заметок по тегам
    """
    result = await NoteORM.tag_search(tags)
    return result
