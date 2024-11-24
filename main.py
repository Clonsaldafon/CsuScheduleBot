import logging
import os

from aiogram import Bot, Dispatcher
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv

from handlers import router


async def main():
    load_dotenv()

    bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    db = Dispatcher(storage=MemoryStorage())
    db.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await db.start_polling(bot, allowed_updates=db.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(main())
