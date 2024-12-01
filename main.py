import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv

from aiogram.fsm.storage.redis import RedisStorage

from database.db import redis_client
from handlers.admin import admin_router
from handlers.group import group_router
from handlers.schedule import schedule_router
from handlers.user import user_router


async def main():
    load_dotenv()

    bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    db = Dispatcher(storage=RedisStorage(redis=redis_client))
    db.include_routers(user_router, admin_router, group_router, schedule_router)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await db.start_polling(
            bot,
            allowed_updates=db.resolve_used_update_types(),
            retry_start=True,
            disable_notification=False,
            timeout=20,
            fast=True
        )
    except Exception as e:
        logging.error(msg=f"An error occurred during polling: {e}")
        await asyncio.sleep(delay=10)
        await main()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(main())
