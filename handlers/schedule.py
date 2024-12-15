import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from consts.bot_answer import SCHEDULE_NO_EXISTS, NOW_FIRST_WEEK, NOW_SECOND_WEEK, \
    TODAY_NO_SUBJECTS, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SUNDAY, SATURDAY, CHOOSE_SCHEDULE_TYPE, \
    SUPPORT_ANSWER
from consts.kb import ButtonText, CallbackData
from database.db import redis_client
from keyboards.inline import schedule_types_kb, back_kb, schedule_types_with_join_kb
from middlewares.auth import auth_middleware
from middlewares.group import group_middleware
from services.schedule import schedule_service
from states.schedule import Schedule


schedule_router = Router()

schedule_router.message.middleware(auth_middleware)
schedule_router.message.middleware(group_middleware)
schedule_router.callback_query.middleware(auth_middleware)
schedule_router.callback_query.middleware(group_middleware)

@schedule_router.message(F.text == ButtonText.SCHEDULE)
async def schedule_handler(msg: Message, state: FSMContext):
    try:
        my_group_id = await redis_client.get(f"my_group_id:{msg.chat.id}")
        if my_group_id:
            await redis_client.set(name=f"group_id:{msg.chat.id}", value=str(my_group_id))

        await msg.answer(text=CHOOSE_SCHEDULE_TYPE, reply_markup=schedule_types_kb())
        await state.set_state(Schedule.schedule_type)
    except Exception as e:
        logging.error(msg=f"Redis error when try getting group_id:{msg.chat.id} in my schedule: {e}")

@schedule_router.callback_query(F.data == CallbackData.BACK_CALLBACK, Schedule.schedule_type_selected)
async def back_schedule_type_selected(call: CallbackQuery, state: FSMContext):
    try:
        if await redis_client.get(f"joined:{call.message.chat.id}") == "true":
            await call.message.edit_text(text=CHOOSE_SCHEDULE_TYPE, reply_markup=schedule_types_kb())
        else:
            await call.message.edit_text(text=CHOOSE_SCHEDULE_TYPE, reply_markup=schedule_types_with_join_kb())
        await state.set_state(Schedule.schedule_type)
    except Exception as e:
        logging.error(msg=f"Redis error when try getting joined:{call.message.chat.id} in back from schedule type: {e}")

@schedule_router.callback_query(F.data == CallbackData.TODAY_CALLBACK, Schedule.schedule_type)
async def today_schedule_handler(call: CallbackQuery, state: FSMContext):
    try:
        is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
        response = await get_schedule(call.message.chat.id, is_even)

        if await is_successful(response, call):
            day_of_week = datetime.today().weekday() + 1
            answer = [NOW_FIRST_WEEK if (not is_even) else NOW_SECOND_WEEK]

            for subject in response["data"]:
                if subject["day_of_week"] == day_of_week:
                    answer += schedule_service.get_info(subject)

            if len(answer) == 1:
                answer.append(TODAY_NO_SUBJECTS)

            answer.append(f"\n\n{SUPPORT_ANSWER}")

            await call.message.edit_text(text="".join(answer), reply_markup=back_kb())
            await state.set_state(Schedule.schedule_type_selected)
    except Exception as e:
        logging.error(msg=f"Error when getting today schedule for user {call.message.chat.id}: {e}")

@schedule_router.callback_query(F.data.in_({
    CallbackData.WEEK_CALLBACK,
    CallbackData.NEXT_WEEK_CALLBACK
}), Schedule.schedule_type)
async def week_schedule_handler(call: CallbackQuery, state: FSMContext):
    try:
        is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
        if call.data == CallbackData.NEXT_WEEK_CALLBACK:
            is_even = not is_even
        response = await get_schedule(call.message.chat.id, is_even)

        if await is_successful(response, call):
            answer = get_week_schedule_info(response, is_even)

            await call.message.edit_text(text=answer, reply_markup=back_kb())
            await state.set_state(Schedule.schedule_type_selected)
    except Exception as e:
        logging.error(msg=f"Error when getting week schedule for user {call.message.chat.id}: {e}")

async def get_schedule(chat_id: int, is_even: bool):
    try:
        token = await redis_client.get(f"chat_id:{chat_id}")
        group_id = await redis_client.get(f"group_id:{chat_id}")

        try:
            return await schedule_service.get_schedule(token=token, group_id=group_id, is_even=is_even)
        except Exception as e:
            logging.error(msg=f"Error when try to get schedule for user {chat_id}: {e}")
            return dict()
    except Exception as e:
        logging.error(msg=f"Redis error when try to get schedule for user {chat_id}: {e}")
        return dict()

async def is_successful(response, call: CallbackQuery):
    if "data" in response:
        if response["data"] is None:
            await call.message.edit_text(text=SCHEDULE_NO_EXISTS, reply_markup=back_kb())
            return False
    return True

def get_week_schedule_info(response, is_even):
    answer = NOW_FIRST_WEEK if (not is_even) else NOW_SECOND_WEEK
    last_day = 0
    week_days = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]

    for subject in response["data"]:
        if last_day != subject["day_of_week"]:
            answer += week_days[subject["day_of_week"] - 1]
            answer += "\n"
            last_day = subject["day_of_week"]
        answer += schedule_service.get_info(subject)

    answer += f"\n\n{SUPPORT_ANSWER}"

    return answer
