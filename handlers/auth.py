import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from consts.bot_answer import START_COMMAND, FEEDBACK_LATER
from consts.kb import CallbackData
from database.db import redis_client
from middlewares.auth import auth_middleware
from middlewares.group import group_middleware


auth_router = Router()

auth_router.message.middleware(auth_middleware)
auth_router.message.middleware(group_middleware)
auth_router.callback_query.middleware(auth_middleware)
auth_router.callback_query.middleware(group_middleware)

@auth_router.message(Command(START_COMMAND))
async def start_handler(msg: Message):
    try:
        if await redis_client.get(name=f"started_at:{msg.chat.id}"):
            return

        await redis_client.set(name=f"started_at:{msg.chat.id}", value=str(datetime.now()))
    except Exception as e:
        logging.error(msg=f"Redis error: {e}")

@auth_router.callback_query(F.data == CallbackData.FEEDBACK_LATER_CALLBACK)
async def feedback_rejection_handler(call: CallbackQuery):
    try:
        await redis_client.set(name=f"started_at:{call.message.chat.id}", value=str(datetime.now()))

        await call.message.answer(text=FEEDBACK_LATER)
    except Exception as e:
        logging.error(msg=f"Redis error: {e}")
