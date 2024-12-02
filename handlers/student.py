from aiogram import Router, F
from aiogram.types import Message

from consts.bot_answer import SOMETHING_WITH_MY_MEMORY
from consts.error import ErrorMessage
from consts.kb import ButtonText
from database.db import redis_client
from keyboards.inline import auth_kb
from keyboards.reply import subscribed_kb, no_subscribed_kb
from services.user import UserService

student_router = Router()
user_service = UserService()

@student_router.message(F.text == ButtonText.MY_PROFILE)
async def my_profile_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        is_subscribed = await redis_client.get(f"subscribed:{msg.chat.id}")
        kb = subscribed_kb if (is_subscribed == "true") else no_subscribed_kb

        response = await user_service.who(token)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=auth_kb())
        else:
            is_notifications_enabled = response["data"]["notifications_enabled"]

            answer = f"<b>ФИО:</b> {response["data"]["full_name"]}\n"
            answer += f"<b>Имя пользователя:</b> @{response["data"]["telegram_username"]}\n"
            answer += f"Уведомления: {"включены" if is_notifications_enabled else "отключены"}\n"
            if is_notifications_enabled:
                answer += f"Уведомлять за <b>{response["data"]["notifications_delay"]} мин.</b> до пары"

            await msg.answer(text=answer, reply_markup=kb())
    except Exception as e:
        print(e)