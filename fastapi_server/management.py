import datetime
from sqlalchemy import select
from fastapi_server.models import Notes, Tags, new_session
from fastapi_server.schemas import NoteAdd, NoteFix, TagSearch
import fastapi_users

class NoteORM:

    @classmethod
    async def add_one(cls, data: NoteAdd, id : int):
        async with new_session() as session:
            print(id)
            note_dict = data.model_dump()
            tags_dict = note_dict.pop('tags')
            note = Notes(**note_dict)
            note.user_id = id
            session.add(note)
            await session.flush()
            await session.commit()
            for obj in tags_dict:
                obj.update({'note_id':note.id})
                tag = Tags(**obj)
                session.add(tag)
            await session.flush()
            await session.commit()
            return 'ok'

    @classmethod
    async def get_all(cls):
        async with new_session() as session:
            query = select(Notes)
            result = await session.execute(query)
            notes = result.scalars().all()
            notes = [_.to_dict() for _ in notes]
            for note in notes:
                query = select(Tags).where(Tags.note_id == note['id'])
                result = await session.execute(query)
                tags = result.scalars().all()
                note.update({'tags':tags})
            return notes
        
    @classmethod
    async def get_one(cls, id):
        async with new_session() as session:
            query = select(Notes).where(Notes.id == id)
            result = await session.execute(query)
            note = result.scalars().first()
            if note is None:
                return 'not found'
            note = note.to_dict()   
            query = select(Tags).where(Tags.note_id == note['id'])
            result = await session.execute(query)
            tags = result.scalars().all()
            note.update({'tags':tags})
            return note
        
    @classmethod
    async def update_one(cls, id, data : NoteAdd, user):
        async with new_session() as session:
            print(user)
            note_dict = data.model_dump()
            tags_dict = note_dict.pop('tags')
            query = select(Notes).where(Notes.id == id)
            result = await session.execute(query)
            note = result.scalars().first()
            if note is None:
                return 'not found'
            if note.user_id != user.id:
                return "not allowed"
            note_dict.update({'last_update':datetime.datetime.now()})
            for key, value in note_dict.items():
                setattr(note, key, value)
            query = select(Tags).where(Tags.note_id == id)
            result = await session.execute(query)
            tags = result.scalars().all()
            for tag in tags:
                await session.delete(tag)
            await session.flush()
            await session.commit()
            for obj in tags_dict:
                obj.update({'note_id':id})
                tag = Tags(**obj)
                session.add(tag)
            await session.flush()
            await session.commit()
            output = note.to_dict()
            output_tags = []
            query = select(Tags).where(Tags.note_id == id)
            result = await session.execute(query)
            tags = result.scalars().all()
            for tag in tags:
                output_tags.append({"id":tag.id, 'name':tag.name, 'note_id':tag.note_id})
            output.update({"tags":output_tags})
            return output

    @classmethod
    async def fix_one(cls, id, data : NoteFix, user_id : int):
        async with new_session() as session:
            note_dict = data.model_dump()
            tags_dict = note_dict.pop('tags')
            query = select(Notes).where(Notes.id == id)
            result = await session.execute(query)
            note = result.scalars().first()
            if note is None:
                return 'not found'
            if note.user_id != user_id:
                return "not allowed"
            note_dict.update({'last_update':datetime.datetime.now()})
            for key, value in note_dict.items():
                setattr(note, key, value) if value else None
            query = select(Tags).where(Tags.note_id == id)
            result = await session.execute(query)
            tags = result.scalars().all()
            for tag in tags:
                await session.delete(tag)
            await session.flush()
            await session.commit()
            if tags_dict is not None:
                for obj in tags_dict:
                    obj.update({'note_id':id})
                    tag = Tags(**obj)
                    session.add(tag)
            await session.flush()
            await session.commit()
            output = note.to_dict()
            output_tags = []
            query = select(Tags).where(Tags.note_id == id)
            result = await session.execute(query)
            tags = result.scalars().all()
            for tag in tags:
                output_tags.append({"id":tag.id, 'name':tag.name, 'note_id':tag.note_id})
            output.update({"tags":output_tags})
            return output
        
    @classmethod
    async def delete_one(cls, id, user_id):
        async with new_session() as session:
            query = select(Notes).where(Notes.id == id)
            result = await session.execute(query)
            note = result.scalars().first()
            if note is None:
                return 'not found'
            if note.user_id != user_id:
                return "not_allowed"
            await session.delete(note)
            await session.commit()
            return 'ok'
        
    @staticmethod
    async def find_child_tags(note : Notes):
        async with new_session() as session:
            query = select(Tags).where(Tags.note_id == note.id)
            result = await session.execute(query)
            result = result.scalars().all()
            return result

    @classmethod
    async def tag_search(cls, tags : TagSearch):
        async with new_session() as session:
            tag_dict = tags.model_dump()
            broken_tags = []
            for tag in tag_dict['tags']:
                query = select(Tags).where(Tags.name == tag)
                result = await session.execute(query)
                result = result.scalars().all()
                if len(result) == 0:
                    broken_tags.append(tag)
            for tag in broken_tags:
                tag_dict['tags'].remove(tag)
            query = select(Notes)
            result = await session.execute(query)
            result = result.scalars().all()
            output_notes = []
            print(tag_dict['tags'])
            if len(tag_dict['tags']) > 0:
                for note in result:
                    child_tags = await NoteORM.find_child_tags(note)
                    names = [tag.name for tag in child_tags]
                    if set(tag_dict['tags']).issubset(set(names)):
                        tmp = note.to_dict()
                        query = select(Tags).where(Tags.note_id == note.id)
                        result = await session.execute(query)
                        result = result.scalars().all()
                        tag_list = []
                        for tag in result:
                            tag_list.append({"name" : tag.name, "id":tag.id, "note_id":tag.note_id})
                        tmp.update({'tags':tag_list})
                        output_notes.append(tmp)
            return output_notes
                
