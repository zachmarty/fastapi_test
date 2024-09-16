from fastapi import APIRouter, Depends

from management import NoteORM
from schemas import NoteAdd, NoteFix, TagSearch

router = APIRouter(
    prefix='/notes',
    tags=['Notes',]
)

@router.get("/")
async def get_notes():
    notes = await NoteORM.get_all()
    return {'data' : notes}

@router.post('/')
async def add_note(
    note :NoteAdd
):
    await NoteORM.add_one(note)
    return 'ok'

@router.get('/{id}')
async def get_note(id : int):
    result = await NoteORM.get_one(id)
    return result

@router.put('/{id}')
async def update_note(id : int, note : NoteAdd):
    result = await NoteORM.update_one(id, note)
    return result

@router.patch('/{id}')
async def fix_note(id : int, note: NoteFix):
    result = await NoteORM.fix_one(id, note)
    return result

@router.delete('/{id}')
async def delete_one(id : int):
    result = await NoteORM.delete_one(id)
    return result

@router.post('/search')
async def tag_search(tags:TagSearch):
    result = await NoteORM.tag_search(tags)
    return result

