import logging

from aiogram import BaseMiddleware
from aiogram.types import ReplyKeyboardRemove, Update, CallbackQuery, Message

from consts.bot_answer import HELLO_ANSWER, START_ANSWER, AUTHORIZATION_ERROR, REGISTRATION_ERROR, \
    SUPPORT_ANSWER
from consts.error import ErrorMessage
from database.db import redis_client
from keyboards.reply import no_joined_kb
from services.auth import auth_service


class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message
        else:
            return await handler(event, data)

        try:
            token = await redis_client.get(name=f"chat_id:{message.chat.id}")

            if not token:
                try:
                    response = await auth_service.log_in_student(telegram=message.chat.id)

                    if "data" in response:
                        if "access_token" in response["data"]:
                            token = response["data"]["access_token"]

                            await redis_client.set(name=f"chat_id:{message.chat.id}", value=str(token))
                        elif "error" in response["data"]:
                            match response["data"]["error"]:
                                case ErrorMessage.USER_NOT_FOUND:
                                    response = await auth_service.sign_up_student(
                                        fullname="#",
                                        telegram=message.chat.id,
                                        username=message.chat.username
                                    )

                                    if "data" in response:
                                        if "access_token" in response["data"]:
                                            token = response["data"]["access_token"]

                                            await redis_client.set(name=f"chat_id:{message.chat.id}", value=str(token))

                                            await message.answer(text=HELLO_ANSWER)
                                            await message.answer(text=START_ANSWER, reply_markup=no_joined_kb())
                                            await message.answer(text=SUPPORT_ANSWER)

                                            return
                                        elif "error" in response["data"]:
                                            await message.answer(text=REGISTRATION_ERROR)

                                            return
                        else:
                            await message.answer(text=HELLO_ANSWER, reply_markup=ReplyKeyboardRemove())

                            return
                except Exception as e:
                    logging.error(msg=f"Error during authorization for user {message.chat.id}: {e}")

                    await message.answer(text=AUTHORIZATION_ERROR)

                    return

            return await handler(event, data)
        except Exception as e:
            logging.error(msg=f"Redis error when try getting chat_id:{message.chat.id} in auth middleware: {e}")


auth_middleware = AuthMiddleware()
