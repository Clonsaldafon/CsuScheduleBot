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
from handlers.feedback import survey_check_loop
from handlers.group import group_router
from handlers.schedule import schedule_router
from handlers.student import student_router
from handlers.user import user_router


async def shutdown(bot: Bot, dp: Dispatcher):
    await dp.storage.close()
    await bot.session.close()

async def start_polling(bot: Bot, dp: Dispatcher):
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            retry_start=True,
            disable_notification=False,
            timeout=20,
            fast=True
        )
    except Exception as e:
        logging.error(f"Error when starting polling: {e}")
        raise

async def delete_webhook(bot: Bot):
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.error(f"Error when deleting a webhook: {e}")
        raise

async def main():
    load_dotenv()

    bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=RedisStorage(redis=redis_client))
    dp.include_routers(user_router, admin_router, student_router, group_router, schedule_router)

    tasks = [
        asyncio.create_task(delete_webhook(bot)),
        asyncio.create_task(start_polling(bot, dp)),
        asyncio.create_task(survey_check_loop(bot))
    ]

    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"A critical error has occurred: {e}")
    finally:
        await shutdown(bot, dp)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(main())
