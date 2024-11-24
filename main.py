import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv

from handlers import router

from aiogram.fsm.storage.redis import RedisStorage

from db import redis_client


async def main():
    load_dotenv()

    bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    db = Dispatcher(storage=RedisStorage(redis=redis_client))
    db.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await db.start_polling(bot, allowed_updates=db.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(main())
