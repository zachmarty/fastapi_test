import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime
from sqlalchemy.sql import func

engine = create_async_engine(
    "sql+aiosqlite:///proj.db"
)

new_session = async_sessionmaker(engine, expire_on_commit = False)

class Base(DeclarativeBase):
    pass

class Notes(Base):
    __tablename__ = "notes"

    id:Mapped[int] = mapped_column(primary_key = True)
    name:Mapped[str] = mapped_column(String(50))
    content:Mapped[str] = mapped_column(Text(1000))
    creation_date:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default = func.now())
    last_update:Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default = func.now())

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)