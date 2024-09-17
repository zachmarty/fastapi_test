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


@router.get("/")
async def get_notes(user: User = Depends(current_user)):
    notes = await NoteORM.get_all()
    return {"data": notes}


@router.post("/")
async def add_note(note: NoteAdd, user: User = Depends(current_user)):
    print(user.id)
    await NoteORM.add_one(note, user.id)
    return "ok"


@router.get("/{id}")
async def get_note(id: int, user: User = Depends(current_user)):
    result = await NoteORM.get_one(id)
    return result


@router.put("/{id}")
async def update_note(id: int, note: NoteAdd, user: User = Depends(current_user)):
    result = await NoteORM.update_one(id, note, user.id)
    return result


@router.patch("/{id}")
async def fix_note(id: int, note: NoteFix, user: User = Depends(current_user)):
    result = await NoteORM.fix_one(id, note, user.id)
    return result


@router.delete("/{id}")
async def delete_one(id: int, user: User = Depends(current_user)):
    result = await NoteORM.delete_one(id, user.id)
    return result


@router.post("/search")
async def tag_search(tags: TagSearch, user: User = Depends(current_user)):
    result = await NoteORM.tag_search(tags)
    return result
