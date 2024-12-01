from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message

from consts.bot_answer import SOMETHING_WITH_MY_MEMORY, SCHEDULE_NO_EXISTS, NOW_FIRST_WEEK, NOW_SECOND_WEEK, \
    TODAY_NO_SUBJECTS, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SUNDAY, SATURDAY
from consts.error import ErrorMessage
from consts.kb import ButtonText
from database.db import redis_client
from keyboards.inline import auth_kb
from keyboards.reply import no_subscribed_kb, subscribed_kb
from services.schedule import ScheduleService

schedule_router = Router()
schedule_service = ScheduleService()

@schedule_router.message(F.text == ButtonText.TODAY_SCHEDULE)
async def today_schedule_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        group_id = await redis_client.get(f"group_id:{msg.chat.id}")
        is_subscribed = await redis_client.get(f"subscribed:{msg.chat.id}")
        kb = subscribed_kb if (is_subscribed == "true") else no_subscribed_kb

        response = await schedule_service.get_for_today(token=token, group_id=group_id)

        if response["data"] is None:
            await msg.answer(text=SCHEDULE_NO_EXISTS, reply_markup=kb())
        elif "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=auth_kb())
        else:
            is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
            day_of_week = datetime.today().weekday() + 1
            answer = [NOW_FIRST_WEEK if (not is_even) else NOW_SECOND_WEEK]

            for subject in response["data"]:
                if subject["is_even"] == is_even:
                    if subject["day_of_week"] == day_of_week:
                        answer += schedule_service.get_info(subject)

            if len(answer) == 1:
                answer.append(TODAY_NO_SUBJECTS)

            await msg.answer(text="".join(answer), reply_markup=kb())
    except Exception as e:
        print(e)

@schedule_router.message(F.text == ButtonText.WEEK_SCHEDULE)
async def today_schedule_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        group_id = await redis_client.get(f"group_id:{msg.chat.id}")
        is_subscribed = await redis_client.get(f"subscribed:{msg.chat.id}")
        kb = subscribed_kb if (is_subscribed == "true") else no_subscribed_kb

        response = await schedule_service.get_for_week(token=token, group_id=group_id)

        if response["data"] is None:
            await msg.answer(text=SCHEDULE_NO_EXISTS, reply_markup=kb())
        elif "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.delete_reply_markup()
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=auth_kb())
        else:
            is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
            answer = NOW_FIRST_WEEK if (not is_even) else NOW_SECOND_WEEK
            last_day = 0
            week_days = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]

            for subject in response["data"]:
                if last_day != subject["day_of_week"]:
                    answer += week_days[subject["day_of_week"] - 1]
                    answer += "\n"
                    last_day = subject["day_of_week"]
                answer += schedule_service.get_info(subject)

            await msg.answer(text=answer, reply_markup=kb())
    except Exception as e:
        print(e)
