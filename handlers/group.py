from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from consts.bot_answer import SOMETHING_WITH_MY_MEMORY, CHOOSE_YOUR_FACULTY, CHOOSE_YOUR_PROGRAM, \
    GROUPS_WILL_BE_HERE_SOON, CHOOSE_YOUR_GROUP, NOW_YOU_CAN_VIEW_SCHEDULE, SOMETHING_WENT_WRONG, \
    YOU_JOINED_SUCCESSFUL, YOUR_GROUPS, YOU_CAN_FIND_GROUP_AGAIN, YOU_LEAVED_SUCCESSFUL, CHOOSE_YOUR_ROLE_AGAIN, \
    YOU_ARE_ALREADY_JOINED, CHOOSE_SCHEDULE_TYPE
from consts.error import ErrorMessage
from consts.kb import ButtonText, CallbackData
from database.db import redis_client
from keyboards.reply import no_joined_kb, choose_faculty_kb, joined_kb
from services.university_structure import UniversityStructureService
from services.group import GroupService
from states.group import Group
from keyboards.inline import all_groups_kb, faculties_with_id_kb, programs_kb, roles_kb, schedule_types_kb

group_router = Router()
group_service = GroupService()
university_structure_service = UniversityStructureService()
all_groups = dict()

@group_router.message(F.text.in_({
    ButtonText.CHOOSE_FACULTY,
    ButtonText.ANOTHER_GROUP_SCHEDULE
}))
async def choose_faculty_handler(msg: Message, state: FSMContext):
    await redis_client.set(
        name=f"another_group:{msg.chat.id}",
        value=str(msg.text == ButtonText.ANOTHER_GROUP_SCHEDULE)
    )

    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        response = await university_structure_service.get_faculties(token)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=choose_faculty_kb())

            await state.clear()
        else:
            faculties = dict()
            for faculty in response["data"]:
                faculties[faculty["name"]] = faculty["faculty_id"]

            await msg.answer(text=CHOOSE_YOUR_FACULTY, reply_markup=faculties_with_id_kb(faculties))
            await state.set_state(Group.faculty)
    except Exception as e:
        print(e)

@group_router.callback_query(F.data, Group.faculty)
async def capture_faculty(call: CallbackQuery, state: FSMContext):
    faculty_id = call.data
    await state.update_data(faculty_id=faculty_id)

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await university_structure_service.get_programs(token, faculty_id)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await call.message.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await call.message.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=choose_faculty_kb())
            await state.clear()
        else:
            programs = list()
            for program in response["data"]:
                programs.append(program["name"])

            await call.message.edit_text(text=CHOOSE_YOUR_PROGRAM, reply_markup=programs_kb(programs))
            await state.set_state(Group.program)
    except Exception as e:
        print(e)


@group_router.callback_query(F.data != CallbackData.BACK_CALLBACK, Group.program)
async def capture_program(call: CallbackQuery, state: FSMContext):
    program = call.data
    await state.update_data(program=program)

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await group_service.get_groups(token, program)

        if response["data"] is None:
            if await redis_client.get(f"another_group:{call.message.chat.id}") == "True":
                await call.message.answer(text=GROUPS_WILL_BE_HERE_SOON, reply_markup=joined_kb())
            else:
                await call.message.answer(text=GROUPS_WILL_BE_HERE_SOON, reply_markup=choose_faculty_kb())
            await state.clear()
        elif "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await call.message.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await call.message.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=choose_faculty_kb())
            await state.clear()
        else:
            groups = dict()
            for group in response["data"]:
                groups[group["short_name"]] = group["group_id"]

            await call.message.edit_text(text=CHOOSE_YOUR_GROUP, reply_markup=all_groups_kb(groups))
            await state.set_state(Group.group_id)
    except Exception as e:
        print(e)

@group_router.callback_query(F.data == CallbackData.BACK_CALLBACK, Group.program)
async def back_program_handler(call: CallbackQuery, state: FSMContext):
    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await university_structure_service.get_faculties(token)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await call.message.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await call.message.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=choose_faculty_kb())
            await state.clear()
        else:
            faculties = dict()
            for faculty in response["data"]:
                faculties[faculty["name"]] = faculty["faculty_id"]

            await call.message.edit_text(text=CHOOSE_YOUR_FACULTY, reply_markup=faculties_with_id_kb(faculties))
            await state.set_state(Group.faculty)
    except Exception as e:
        print(e)

@group_router.callback_query(F.data != CallbackData.BACK_CALLBACK, Group.group_id)
async def capture_group(call: CallbackQuery, state: FSMContext):
    group_id = call.data
    await state.update_data(group_id=group_id)

    is_another_group = await redis_client.get(name=f"another_group:{call.message.chat.id}")
    if is_another_group == "True":
        await redis_client.set(name=f"another_group_id:{call.message.chat.id}", value=str(group_id))
        await call.message.answer(text=CHOOSE_SCHEDULE_TYPE, reply_markup=schedule_types_kb())
    else:
        await redis_client.set(name=f"group_id:{call.message.chat.id}", value=str(group_id))
        await call.message.answer(text=NOW_YOU_CAN_VIEW_SCHEDULE, reply_markup=no_joined_kb())

    await state.clear()

@group_router.callback_query(F.data == CallbackData.BACK_CALLBACK, Group.group_id)
async def back_group_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(Group.program)
    faculty_id = await state.get_value("faculty_id")

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await university_structure_service.get_programs(token, faculty_id)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await call.message.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await call.message.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=choose_faculty_kb())
            await state.clear()
        else:
            programs = list()
            for program in response["data"]:
                programs.append(program["name"])

            await call.message.edit_text(text=CHOOSE_YOUR_PROGRAM, reply_markup=programs_kb(programs))
            await state.set_state(Group.program)
    except Exception as e:
        print(e)

@group_router.message(F.text == ButtonText.JOIN_TO_GROUP)
async def group_join_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        group_id = await redis_client.get(f"group_id:{msg.chat.id}")

        response = await group_service.join(token=token, group_id=group_id)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case ErrorMessage.YOU_ARE_ALREADY_IN_GROUP:
                    await msg.answer(text=YOU_ARE_ALREADY_JOINED, reply_markup=joined_kb())
                case _:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=no_joined_kb())
        else:
            await redis_client.set(name=f"joined:{msg.chat.id}", value="true")
            await msg.answer(
                text=YOU_JOINED_SUCCESSFUL,
                reply_markup=joined_kb()
            )
    except Exception as e:
        print(e)

@group_router.message(F.text == ButtonText.MY_GROUP)
async def my_group_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        is_joined = await redis_client.get(f"joined:{msg.chat.id}")
        kb = joined_kb if (is_joined == "true") else no_joined_kb

        response = await group_service.get_my(token)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=joined_kb())
        elif "group_id" in response["data"]:
            answer = group_service.get_info(response["data"])

            await msg.answer(text=answer,reply_markup=kb())
        else:
            answer = YOUR_GROUPS
            for group in response["data"]:
                answer += group_service.get_info(group)

            await msg.answer(text=answer, reply_markup=kb())
    except Exception as e:
        print(e)

@group_router.message(F.text == ButtonText.BACK_TO_GROUP_CHOICE)
async def back_group_handler(msg: Message, state: FSMContext):
    await msg.answer(text=YOU_CAN_FIND_GROUP_AGAIN, reply_markup=choose_faculty_kb())
    await state.set_state(Group.faculty)

@group_router.message(F.text == ButtonText.LEAVE_GROUP)
async def leave_group_handler(msg: Message):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        response = await group_service.leave(token)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=joined_kb())
        else:
            await redis_client.set(name=f"joined:{msg.chat.id}", value="false")
            await msg.answer(text=YOU_LEAVED_SUCCESSFUL, reply_markup=no_joined_kb())
    except Exception as e:
        print(e)
