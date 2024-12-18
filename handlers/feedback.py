import asyncio
import logging
from datetime import datetime, timedelta

from consts.bot_answer import FEEDBACK
from database.db import redis_client

from aiogram import Bot

from keyboards.inline import feedback_kb


async def send_survey_invitation(bot: Bot, chat_id: int):
    try:
        await bot.send_message(chat_id=chat_id, text=FEEDBACK, reply_markup=feedback_kb())
    except Exception as e:
        logging.error(msg=f"Failed to send a feedback message to the user {chat_id}: {e}")

async def survey_check_loop(bot):
    while True:
        try:
            started_keys = await redis_client.keys(pattern="started_at:*")
            for key in started_keys:
                started_at_str = await redis_client.get(key)
                started_at = datetime.now().strptime(started_at_str, "%Y-%m-%d %H:%M:%S.%f")
                if datetime.now() - started_at >= timedelta(days=2):
                    chat_id = int(key.split(":")[1])
                    await send_survey_invitation(bot, chat_id)
                    await redis_client.delete(key)
            await asyncio.sleep(172800)
        except Exception as e:
            logging.error(f"Redis error when try getting keys started_at to send feedback message: {e}")
