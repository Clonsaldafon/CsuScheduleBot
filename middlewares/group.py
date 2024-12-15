import logging

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

from consts.bot_answer import START_ANSWER, STUDENT_LOGGED_IN
from consts.error import ErrorMessage
from database.db import redis_client
from keyboards.reply import joined_kb, no_joined_kb
from services.group import group_service


class GroupMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message
        else:
            return await handler(event, data)

        try:
            group_id = await redis_client.get(name=f"group_id:{message.chat.id}")

            if not group_id:
                token = await redis_client.get(name=f"chat_id:{message.chat.id}")

                try:
                    response = await group_service.get_my(token=token)

                    if "data" in response:
                        if "group_id" in response["data"]:
                            group_id = response["data"]["group_id"]

                            await redis_client.set(name=f"group_id:{message.chat.id}", value=str(group_id))
                            await redis_client.set(name=f"joined:{message.chat.id}", value="true")

                            await message.answer(text=STUDENT_LOGGED_IN, reply_markup=joined_kb())
                        elif "error" in response["data"]:
                            match response["data"]["error"]:
                                case ErrorMessage.MEMBER_NOT_FOUND:
                                    await message.answer(text=START_ANSWER, reply_markup=no_joined_kb())
                                case ErrorMessage.YOU_ARE_ALREADY_IN_GROUP:
                                    await message.answer(text=START_ANSWER, reply_markup=joined_kb())
                except Exception as e:
                    logging.error(
                        msg=f"Error when try getting my group for user {message.chat.id} "\
                            f"in group middleware: {e}"
                    )

            return await handler(event, data)
        except Exception as e:
            logging.error(msg=f"Redis error when try getting group_id:{message.chat.id} in group middleware: {e}")


group_middleware = GroupMiddleware()
