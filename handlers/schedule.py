from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from consts.bot_answer import SOMETHING_WITH_MY_MEMORY, SCHEDULE_NO_EXISTS, NOW_FIRST_WEEK, NOW_SECOND_WEEK, \
    TODAY_NO_SUBJECTS, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SUNDAY, SATURDAY, CHOOSE_SCHEDULE_TYPE, \
    CHOOSE_YOUR_ROLE_AGAIN, SOMETHING_WENT_WRONG
from consts.error import ErrorMessage
from consts.kb import ButtonText, CallbackData
from database.db import redis_client
from keyboards.inline import schedule_types_kb, roles_kb
from keyboards.reply import no_joined_kb, joined_kb
from services.schedule import ScheduleService

schedule_router = Router()
schedule_service = ScheduleService()

@schedule_router.message(F.text == ButtonText.SCHEDULE)
async def schedule_handler(msg: Message):
    await msg.answer(text=CHOOSE_SCHEDULE_TYPE, reply_markup=schedule_types_kb())

@schedule_router.callback_query(F.data == CallbackData.TODAY_CALLBACK)
async def today_schedule_handler(call: CallbackQuery):
    try:
        is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
        result = await get_schedule(call.message.chat.id, is_even)

        if await is_successful(result, call):
            response = result["response"]

            day_of_week = datetime.today().weekday() + 1
            answer = [NOW_FIRST_WEEK if (not is_even) else NOW_SECOND_WEEK]

            for subject in response["data"]:
                if subject["day_of_week"] == day_of_week:
                    answer += schedule_service.get_info(subject)

            if len(answer) == 1:
                answer.append(TODAY_NO_SUBJECTS)

            await call.message.answer(text="".join(answer), reply_markup=result["kb"]())
    except Exception as e:
        print(e)

@schedule_router.callback_query(F.data.in_({
    CallbackData.WEEK_CALLBACK,
    CallbackData.NEXT_WEEK_CALLBACK
}))
async def week_schedule_handler(call: CallbackQuery):
    try:
        is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
        if call.data == CallbackData.NEXT_WEEK_CALLBACK:
            is_even = not is_even
        result = await get_schedule(call.message.chat.id, is_even)

        if await is_successful(result, call):
            answer = get_week_schedule_info(result, is_even)
            await call.message.answer(text=answer, reply_markup=result["kb"]())
    except Exception as e:
        print(e)

async def get_schedule(chat_id: int, is_even: bool):
    token = await redis_client.get(f"chat_id:{chat_id}")
    if await redis_client.get(f"another_group:{chat_id}") == "True":
        group_id = await redis_client.get(f"another_group_id:{chat_id}")
        await redis_client.set(name=f"another_group:{chat_id}", value="False")
    else:
        group_id = await redis_client.get(f"group_id:{chat_id}")
    is_joined = await redis_client.get(f"joined:{chat_id}")

    kb = joined_kb if (is_joined == "true") else no_joined_kb
    response = await schedule_service.get_schedule(token=token, group_id=group_id, is_even=is_even)
    return {
        "is_joined": is_joined,
        "kb": kb,
        "response": response
    }

async def is_successful(result, call: CallbackQuery):
    response = result["response"]
    if response["data"] is None:
        await call.message.answer(text=SCHEDULE_NO_EXISTS, reply_markup=result["kb"]())
        return False
    elif "error" in response["data"]:
        match response["data"]["error"]:
            case ErrorMessage.TOKEN_IS_EXPIRED:
                await call.message.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                await call.message.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
            case _:
                await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=None)
    return True

def get_week_schedule_info(result, is_even):
    response = result["response"]

    answer = NOW_FIRST_WEEK if (not is_even) else NOW_SECOND_WEEK
    last_day = 0
    week_days = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]

    for subject in response["data"]:
        if last_day != subject["day_of_week"]:
            answer += week_days[subject["day_of_week"] - 1]
            answer += "\n"
            last_day = subject["day_of_week"]
        answer += schedule_service.get_info(subject)

    return answer
