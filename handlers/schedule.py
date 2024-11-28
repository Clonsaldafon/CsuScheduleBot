from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import redis_client
from handlers.group import group_service
from keyboards.inline import auth_kb, all_groups_kb
from keyboards.reply import no_subscribed_kb
from service.schedule import ScheduleService
from states.group import Group


schedule_router = Router()
schedule_service = ScheduleService()

@schedule_router.message(F.text == "Расписание на сегодня 🗓")
async def today_schedule_handler(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")

        group_response = await group_service.get_my(token)

        if "error" in group_response:
            match group_response["error"]:
                case "token is expired":
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
        elif "group_id" in group_response:
            response = await schedule_service.get_for_today(
                token=token,
                group_id=group_response["group_id"]
            )

            if response is None:
                await msg.answer(
                    text="Староста еще не загрузил расписание 😪\n" +
                         "Попробуй поторопить его",
                    reply_markup=no_subscribed_kb()
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
                    reply_markup=no_subscribed_kb()
                )
        else:
            my_groups = dict()
            my_group_ids = []
            for group in group_response:
                my_groups[group["short_name"]] = group["group_id"]
                my_group_ids.append(str(group["group_id"]))

            await state.set_state(Group.my_group_id)
            await msg.answer(
                text="Я вижу, что ты состоишь в нескольких группах 🧐\n"
                     "Какое именно расписание ты хочешь посмотреть?",
                reply_markup=all_groups_kb(my_groups)
            )
    except Exception as e:
        print(e)

@schedule_router.message(F.text == "Расписание на неделю 🗓")
async def today_schedule_handler(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        group_response = await group_service.get_my(token)

        if "error" in group_response:
            match group_response["error"]:
                case "token is expired":
                    await msg.delete_reply_markup()
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
        elif "group_id" in group_response:
            response = await schedule_service.get_for_week(
                token=token,
                group_id=group_response["group_id"]
            )

            if response is None:
                await msg.answer(
                    text="Староста еще не загрузил расписание 😪\n" +
                         "Попробуй поторопить его",
                    reply_markup=no_subscribed_kb()
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
                is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
                answer = ""
                last_day = 0

                for subject in response:
                    if subject["is_even"] == is_even:
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
                    reply_markup=no_subscribed_kb()
                )
        else:
            my_groups = dict()
            my_group_ids = []
            for group in group_response:
                my_groups[group["short_name"]] = group["group_id"]
                my_group_ids.append(str(group["group_id"]))

            await state.set_state(Group.my_group_id)
            await msg.answer(
                text="Я вижу, что ты состоишь в нескольких группах 🧐\n"
                     "Какое именно расписание ты хочешь посмотреть?",
                reply_markup=all_groups_kb(my_groups)
            )
    except Exception as e:
        print(e)

@schedule_router.message(F.text == "Подписаться на группу 🔔")
async def group_join_handler(msg: Message, state: FSMContext):
    await msg.answer(
        text="Упс, доступ запрещен 🫣\n"
             "Нужно ввести код. Я уверен, староста тебе поможет 😉"
    )
    await state.set_state(Group.code)

@schedule_router.callback_query(F.data, Group.my_group_id)
async def group_schedule_handler(call: CallbackQuery, state: FSMContext):
    group_id = call.data

    try:
        token = await redis_client.get(f"tg_id:{call.from_user.id}")
        response = await schedule_service.get_for_today(
            token=token,
            group_id=group_id
        )

        if response == "None":
            await call.message.answer(
                text="Староста еще не загрузил расписание 😪\n" +
                     "Попробуй поторопить его",
                reply_markup=no_subscribed_kb()
            )
        elif "error" in response:
            match response["error"]:
                case "token is expired":
                    await call.message.delete_reply_markup()
                    await call.message.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
        else:
            is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
            answer = ""
            last_day = 0

            for subject in response:
                if subject["is_even"] == is_even:
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

            await call.message.answer(
                text=answer,
                reply_markup=no_subscribed_kb()
            )

        await state.clear()
    except Exception as e:
        print(e)
