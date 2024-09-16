from fastapi import FastAPI
from contextlib import asynccontextmanager
from models import create_tables, drop_tables
from router import router as notes_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_tables()
    await create_tables()
    print('created')
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(notes_router)

