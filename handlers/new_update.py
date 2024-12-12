import asyncio
import logging

from aiogram import Bot

from consts.bot_answer import NEW_UPDATE
from consts.error import ErrorMessage
from database.db import redis_client
from keyboards.reply import joined_kb, no_joined_kb
from services.auth import auth_service
from services.group import group_service


chat_ids = [
    929827564, 1031208299, 400216868, 5631147771, 1211007456, 1032199981, 5740628600, 893845029, 1916396726, 945285197,
    406724688, 1109306626, 1082617356, 863442476, 854042318, 6177296237, 1689169332, 1451495673, 935158648, 819612337,
    1108990095, 876218873, 1216034152, 963171423, 1463020923, 1200316920, 351882546, 1047757740, 806719110, 1416861129,
    1699328560, 5129459679, 5795388409, 1028263499, 1776693924, 585265993, 817833250, 1789426376, 2050446892,
    997852253, 476318872, 1333742897, 857602523, 1906737154, 731405562, 1803170713, 1104990894, 6355412127,
    873998359, 5977978555, 374935495, 379799883, 740462955, 852229124, 884913263
]


async def send_new_update_message(bot: Bot):
    try:
        for chat_id in chat_ids:
            joined = await redis_client.get(name=f"joined:{chat_id}")

            if joined is None:
                token = await redis_client.get(name=f"chat_id:{chat_id}")

                if token is None:
                    try:
                        response = await auth_service.log_in_student(chat_id)

                        if "data" in response:
                            if "access_token" in response["data"]:
                                token = response["data"]["access_token"]
                                await redis_client.set(name=f"chat_id:{chat_id}", value=str(token))

                                response = await group_service.get_my(token)

                                if "data" in response:
                                    if "group_id" in response["data"]:
                                        group_id = response["data"]["group_id"]
                                        await redis_client.set(name=f"group_id:{chat_id}", value=str(group_id))
                                        await redis_client.set(name=f"joined:{chat_id}", value="true")
                                        joined = "true"
                                    elif "error" in response["data"]:
                                        if response["data"]["error"] == ErrorMessage.MEMBER_NOT_FOUND:
                                            joined = "false"
                    except Exception as e:
                        logging.error(msg=f"Error with chat_id = {chat_id}: {e}")

            kb = joined_kb if joined == "true" else no_joined_kb

            try:
                await bot.send_message(chat_id=chat_id, text=NEW_UPDATE, reply_markup=kb())
            except Exception as e:
                logging.error(msg=f"Failed to send message to {chat_id} with new update: {e}")
            await asyncio.sleep(1)
    except Exception as e:
        logging.error(msg=f"Redis error: {e}")
