from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import redis_client
from keyboards.reply import no_subscribed_kb, choose_faculty_kb, subscribed_kb
from services.university_structure import UniversityStructureService
from services.group import GroupService
from states.group import Group
from keyboards.inline import auth_kb, all_groups_kb, faculties_kb, programs_kb


group_router = Router()
group_service = GroupService()
university_structure_service = UniversityStructureService()
all_groups = dict()

@group_router.message(F.text == "Выбрать факультет")
async def choose_faculty_handler(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        response = await university_structure_service.get_faculties(token)

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
                    await state.clear()
        else:
            faculties = dict()

            for faculty in response:
                faculties[faculty["name"]] = faculty["faculty_id"]

            await msg.answer(
                text="Выбери свой факультет",
                reply_markup=faculties_kb(faculties)
            )

            await state.set_state(Group.faculty_id)
    except Exception as e:
        print(e)

@group_router.callback_query(F.data, Group.faculty_id)
async def capture_faculty(call: CallbackQuery, state: FSMContext):
    faculty_id = call.data
    await state.update_data(faculty_id=faculty_id)

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await university_structure_service.get_programs(token, faculty_id)

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await call.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
                    await state.clear()
        else:
            programs = []

            for program in response:
                programs.append(program["name"])

            await call.message.edit_text(
                text="Выбери программу обучения",
                reply_markup=programs_kb(programs)
            )

            await state.set_state(Group.program)
    except Exception as e:
        print(e)


@group_router.callback_query(F.data != "back", Group.program)
async def capture_program(call: CallbackQuery, state: FSMContext):
    program = call.data
    await state.update_data(program=program)

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await group_service.get_groups(token, program)

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await call.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
                    await state.clear()
        else:
            groups = dict()

            for group in response:
                groups[group["short_name"]] = group["group_id"]

            await call.message.edit_text(
                text="Выбери свою группу",
                reply_markup=all_groups_kb(groups)
            )

            await state.set_state(Group.group_id)
    except Exception as e:
        print(e)

@group_router.callback_query(F.data == "back", Group.program)
async def back_program_handler(call: CallbackQuery, state: FSMContext):
    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await university_structure_service.get_faculties(token)

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await call.message.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
                    await state.clear()
        else:
            faculties = dict()

            for faculty in response:
                faculties[faculty["name"]] = faculty["faculty_id"]

            await call.message.edit_text(
                text="Выбери свой факультет",
                reply_markup=faculties_kb(faculties)
            )

            await state.set_state(Group.faculty_id)
    except Exception as e:
        print(e)

@group_router.callback_query(F.data != "back", Group.group_id)
async def capture_group(call: CallbackQuery, state: FSMContext):
    group_id = call.data
    await state.update_data(group_id=group_id)

    await redis_client.set(
        name=f"group_id:{call.message.chat.id}",
        value=str(group_id)
    )

    await call.message.answer(
        text="Теперь с помощью кнопок ниже ты можешь смотреть расписание или подписаться на получение уведомлений",
        reply_markup=no_subscribed_kb()
    )
    await state.clear()

@group_router.callback_query(F.data == "back", Group.group_id)
async def back_group_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(Group.program)
    faculty_id = await state.get_value("faculty_id")

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await university_structure_service.get_programs(token, faculty_id)

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await call.message.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
                    await state.clear()
        else:
            programs = []

            for program in response:
                programs.append(program["name"])

            await call.message.edit_text(
                text="Выбери программу обучения",
                reply_markup=programs_kb(programs)
            )

            await state.set_state(Group.program)
    except Exception as e:
        print(e)

@group_router.message(F.text == "Подписаться на группу 🔔")
async def group_join_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        group_id = await redis_client.get(f"group_id:{msg.chat.id}")

        response = await group_service.join(
            token=token,
            group_id=group_id
        )

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await msg.delete_reply_markup()
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
                case _:
                    await msg.answer(
                        text="Похоже, что-то пошло не по плану... 🫣",
                        reply_markup=no_subscribed_kb()
                    )
        else:
            await redis_client.set(
                name=f"subscribed:{msg.chat.id}",
                value="true"
            )
            await msg.answer(
                text=f"Welcome! 🥳",
                reply_markup=subscribed_kb()
            )
    except Exception as e:
        print(e)

@group_router.message(F.text == "Моя группа 🫂")
async def my_group_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        is_subscribed = await redis_client.get(f"subscribed:{msg.chat.id}")
        response = await group_service.get_my(token)

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
        elif "group_id" in response:
            answer = group_service.get_info(response)

            await msg.answer(
                text=answer,
                reply_markup=subscribed_kb() if (is_subscribed == "true") else no_subscribed_kb()
            )
        else:
            answer = "Вот группы, в которых ты состоишь:\n\n"
            for group in response:
                answer += group_service.get_info(group)

            await msg.answer(
                text=answer,
                reply_markup=subscribed_kb() if (is_subscribed == "true") else no_subscribed_kb()
            )
    except Exception as e:
        print(e)

@group_router.message(F.text == "Вернуться к выбору группы 🔙")
async def back_group_handler(msg: Message, state: FSMContext):
    await msg.answer(
        text="Ты можешь заново найти нужную тебе группу",
        reply_markup=choose_faculty_kb()
    )
    await state.set_state(Group.faculty_id)

@group_router.message(F.text == "Отписаться 🔕")
async def leave_group_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        response = await group_service.leave(token)

        await msg.answer(
            text="Теперь ты не будешь получать уведомления 🫠",
            reply_markup=no_subscribed_kb()
        )

        await redis_client.set(
            name=f"subscribed:{msg.chat.id}",
            value="false"
        )
    except Exception as e:
        print(e)
