from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import redis_client
from handlers.group import group_service
from keyboards.inline import auth_kb, all_groups_kb
from keyboards.reply import no_subscribed_kb, subscribed_kb
from service.schedule import ScheduleService
from states.group import Group


schedule_router = Router()
schedule_service = ScheduleService()

@schedule_router.message(F.text == "Расписание на сегодня 🗓")
async def today_schedule_handler(msg: Message):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        group_id = await redis_client.get(f"group_id:{msg.from_user.id}")
        is_subscribed = await redis_client.get(f"subscribed:{msg.from_user.id}")

        response = await schedule_service.get_for_today(
            token=token,
            group_id=group_id
        )

        if response is None:
            await msg.answer(
                text="Староста еще не загрузил расписание 😪\n" +
                     "Попробуй поторопить его",
                reply_markup=subscribed_kb() if (is_subscribed == "true") else no_subscribed_kb()
            )
        elif "error" in response:
            match response["error"]:
                case "token is expired":
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
        else:
            is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
            day_of_week = datetime.today().weekday() + 1
            answer = ""

            for subject in response:
                if subject["is_even"] == is_even:
                    if subject["day_of_week"] == day_of_week:
                        answer += schedule_service.get_info(subject)

            if answer == "":
                answer = "Сегодня пар нет 🥳"

            await msg.answer(
                text=answer,
                reply_markup=subscribed_kb() if (is_subscribed == "true") else no_subscribed_kb()
            )
    except Exception as e:
        print(e)

@schedule_router.message(F.text == "Расписание на неделю 🗓")
async def today_schedule_handler(msg: Message):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        group_id = await redis_client.get(f"group_id:{msg.from_user.id}")
        is_subscribed = await redis_client.get(f"subscribed:{msg.from_user.id}")

        response = await schedule_service.get_for_week(
            token=token,
            group_id=group_id
        )

        if response is None:
            await msg.answer(
                text="Староста еще не загрузил расписание 😪\n" +
                     "Попробуй поторопить его",
                reply_markup=subscribed_kb() if (is_subscribed == "true") else no_subscribed_kb()
            )
        elif "error" in response:
            match response["error"]:
                case "token is expired":
                    await msg.delete_reply_markup()
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
        else:
            answer = ""
            last_day = 0

            for subject in response:
                if last_day != subject["day_of_week"]:
                    match subject["day_of_week"]:
                        case 1:
                            answer += "<b>🟩🟩🟩 Понедельник 🟩🟩🟩</b>"
                        case 2:
                            answer += "<b>🟩🟩🟩 Вторник 🟩🟩🟩</b>"
                        case 3:
                            answer += "<b>🟩🟩🟩 Среда 🟩🟩🟩</b>"
                        case 4:
                            answer += "<b>🟩🟩🟩 Четверг 🟩🟩🟩</b>"
                        case 5:
                            answer += "<b>🟩🟩🟩 Пятница 🟩🟩🟩</b>"
                        case 6:
                            answer += "<b>🟩🟩🟩 Суббота 🟩🟩🟩</b>"
                    answer += "\n"
                    last_day = subject["day_of_week"]
                answer += schedule_service.get_info(subject)

            await msg.answer(
                text=answer,
                reply_markup=subscribed_kb() if (is_subscribed == "true") else no_subscribed_kb()
            )
    except Exception as e:
        print(e)

# @schedule_router.callback_query(F.data, Group.my_group_id)
# async def group_schedule_handler(call: CallbackQuery, state: FSMContext):
#     group_id = call.data
#
#     try:
#         token = await redis_client.get(f"tg_id:{call.from_user.id}")
#         response = await schedule_service.get_for_today(
#             token=token,
#             group_id=group_id
#         )
#
#         if response == "None":
#             await call.message.answer(
#                 text="Староста еще не загрузил расписание 😪\n" +
#                      "Попробуй поторопить его",
#                 reply_markup=no_subscribed_kb()
#             )
#         elif "error" in response:
#             match response["error"]:
#                 case "token is expired":
#                     await call.message.delete_reply_markup()
#                     await call.message.answer(
#                         text="Ой, что-то случилось с моей памятью 😵‍💫\n"
#                              "Давай начнем сначала ⤵",
#                         reply_markup=auth_kb()
#                     )
#         else:
#             is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
#             answer = ""
#             last_day = 0
#
#             for subject in response:
#                 if subject["is_even"] == is_even:
#                     if last_day != subject["day_of_week"]:
#                         match subject["day_of_week"]:
#                             case 1:
#                                 answer += "<b>🟩🟩🟩 Понедельник 🟩🟩🟩</b>"
#                             case 2:
#                                 answer += "<b>🟩🟩🟩 Вторник 🟩🟩🟩</b>"
#                             case 3:
#                                 answer += "<b>🟩🟩🟩 Среда 🟩🟩🟩</b>"
#                             case 4:
#                                 answer += "<b>🟩🟩🟩 Четверг 🟩🟩🟩</b>"
#                             case 5:
#                                 answer += "<b>🟩🟩🟩 Пятница 🟩🟩🟩</b>"
#                             case 6:
#                                 answer += "<b>🟩🟩🟩 Суббота 🟩🟩🟩</b>"
#                         answer += "\n"
#                         last_day = subject["day_of_week"]
#                     answer += schedule_service.get_info(subject)
#
#             await call.message.answer(
#                 text=answer,
#                 reply_markup=no_subscribed_kb()
#             )
#
#         await state.clear()
#     except Exception as e:
#         print(e)
