from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import redis_client
from keyboards.reply import schedule_kb, choose_faculty_kb
from service.edu import EduService
from service.group import GroupService
from states.group import Group
from keyboards.inline import auth_kb, all_groups_kb, faculties_kb, programs_kb


group_router = Router()
group_service = GroupService()
edu_service = EduService()
all_groups = dict()

@group_router.message(F.text == "Выбрать факультет")
async def choose_faculty_handler(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        response = await edu_service.get_faculties(token)

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
        token = await redis_client.get(f"tg_id:{call.from_user.id}")
        response = await edu_service.get_programs(token, faculty_id)

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
        token = await redis_client.get(f"tg_id:{call.from_user.id}")
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
        token = await redis_client.get(f"tg_id:{call.from_user.id}")
        response = await edu_service.get_faculties(token)

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

    await call.message.answer(
        text="Упс, доступ запрещен 🫣\n"
             "Нужно ввести код. Я уверен, староста тебе поможет 😉"
    )
    await state.set_state(Group.code)

@group_router.callback_query(F.data == "back", Group.group_id)
async def back_group_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(Group.program)
    faculty_id = await state.get_value("faculty_id")

    try:
        token = await redis_client.get(f"tg_id:{call.from_user.id}")
        response = await edu_service.get_programs(token, faculty_id)

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

@group_router.message(F.text, Group.code)
async def capture_code(msg: Message, state: FSMContext):
    code = msg.text

    await state.update_data(code=code)
    await msg.delete()

    try:
        data = await state.get_data()
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")

        response = await group_service.join(
            token=token,
            group_id=data.get("group_id"),
            code=code
        )

        if "error" in response:
            match response["error"]:
                case "wrong group code" | "access denied":
                    await msg.answer(
                        text="Интересно, кто из вас ошибся? 🤔\n" +
                             "Попробуй ввести код еще раз",
                        reply_markup=all_groups_kb(all_groups)
                    )
                    await state.set_state(Group.code)
                case "token is expired":
                    await msg.delete_reply_markup()
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
                    await state.clear()
                case _:
                    await msg.answer(
                        text="Похоже, что-то пошло не по плану... 🫣\n" +
                             "Попробуй ввести код еще раз ✍",
                        reply_markup=all_groups_kb(all_groups)
                    )
                    await state.set_state(Group.code)
        else:
            await redis_client.set(name=f"group_id:{msg.from_user.id}", value=f"{data.get("id")}")
            await msg.answer(text=f"Welcome! 🥳", reply_markup=schedule_kb())
            await state.clear()
    except Exception as e:
        print(e)

@group_router.message(F.text == "Моя группа 🫂")
async def my_group_handler(msg: Message):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
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
                reply_markup=schedule_kb()
            )
        else:
            answer = "Вот группы, в которых ты состоишь:\n\n"
            for group in response:
                answer += group_service.get_info(group)

            await msg.answer(
                text=answer,
                reply_markup=schedule_kb()
            )
    except Exception as e:
        print(e)

@group_router.message(F.text == "Покинуть группу ❌")
async def leave_group_handler(msg: Message):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        response = await group_service.leave(token)

        await msg.answer(
            text="Надеюсь, ты не забыл попрощаться с одногруппниками? 🫠",
            reply_markup=choose_faculty_kb()
        )
    except Exception as e:
        print(e)
