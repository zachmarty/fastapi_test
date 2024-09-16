import asyncio
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
import os
from aioredis import Redis
from dotenv import load_dotenv
from telegram_bot.handlers import message_router
from aiogram.fsm.storage.redis import RedisStorage

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
TOKEN = os.getenv("BOT_TOKEN")
SITE_URL = os.getenv("SITE_URL")
cookie_jwt = ""

bot = Bot(token=TOKEN)
redis = Redis()
dp = Dispatcher(storage=RedisStorage(redis = redis))
dp.include_router(message_router)
logging.basicConfig(level=logging.INFO)

dp.start_polling(bot)


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
