from fastapi import FastAPI
from contextlib import asynccontextmanager

from models import create_tables, drop_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await drop_tables()
    print('clear')
    await create_tables()
    print('created')
    yield

app = FastAPI(lifespan=lifespan)