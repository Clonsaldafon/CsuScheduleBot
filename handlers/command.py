import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from consts.bot_answer import HELP_COMMAND, HELP_ANSWER, SUPPORT_COMMAND, SUPPORT_ANSWER, FEEDBACK_COMMAND, \
    FEEDBACK_ANSWER
from database.db import redis_client
from keyboards.reply import joined_kb, no_joined_kb

command_router = Router()

@command_router.message(Command(HELP_COMMAND))
async def help_handler(msg: Message):
    try:
        kb = joined_kb if await redis_client.get(f"joined:{msg.chat.id}") == "true" else no_joined_kb
        await msg.answer(text=HELP_ANSWER, reply_markup=kb())
    except Exception as e:
        logging.error(msg=f"Redis error when try getting joined:{msg.chat.id} after click on /help: {e}")

@command_router.message(Command(SUPPORT_COMMAND))
async def support_handler(msg: Message):
    try:
        kb = joined_kb if await redis_client.get(f"joined:{msg.chat.id}") == "true" else no_joined_kb
        await msg.answer(text=SUPPORT_ANSWER, reply_markup=kb())
    except Exception as e:
        logging.error(msg=f"Redis error when try getting joined:{msg.chat.id} after click on /support: {e}")

@command_router.message(Command(FEEDBACK_COMMAND))
async def feedback_handler(msg: Message):
    try:
        kb = joined_kb if await redis_client.get(f"joined:{msg.chat.id}") == "true" else no_joined_kb
        await msg.answer(text=FEEDBACK_ANSWER, reply_markup=kb())
    except Exception as e:
        logging.error(msg=f"Redis error when try getting joined:{msg.chat.id} after click on /feedback: {e}")
