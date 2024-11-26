import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv

from aiogram.fsm.storage.redis import RedisStorage

from db import redis_client
from handlers.group import group_router
from handlers.schedule import schedule_router
from handlers.user import user_router


async def main():
    load_dotenv()

    bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    db = Dispatcher(storage=RedisStorage(redis=redis_client))
    db.include_routers(user_router, group_router, schedule_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await db.start_polling(bot, allowed_updates=db.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(main())
