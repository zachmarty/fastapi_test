import datetime
from typing import List, Optional
from pydantic import BaseModel


class TagBase(BaseModel):
    id: int
    name: str
    note_id: int


class TagAdd(BaseModel):
    name: str


class NoteBase(BaseModel):
    id: int
    name: str
    content: str
    creation_date: datetime.datetime
    last_update: datetime.datetime
    tags: List[TagBase]


class NoteAdd(BaseModel):
    name: str
    content: str
    tags: List[TagAdd]


class NoteFix(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[TagAdd]] = None


class NoteList(BaseModel):
    notes: List[NoteBase]


class TagSearch(BaseModel):
    tags: List[str]
