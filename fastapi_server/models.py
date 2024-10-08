import datetime
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True)

new_session = async_sessionmaker(engine, expire_on_commit=False)

"""
Файл с описанием моделей заметок и тегов
"""


class Base(DeclarativeBase):
    pass


class Notes(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_update: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[int]
    tags = relationship("Tags", back_populates="note", cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "creation_date": self.creation_date,
            "last_update": self.last_update,
        }


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id"))

    note = relationship("Notes", back_populates="tags")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
