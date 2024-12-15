import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from consts.bot_answer import CHOOSE_FACULTY, CHOOSE_PROGRAM, \
    GROUPS_WILL_BE_HERE_SOON, CHOOSE_GROUP, SOMETHING_WENT_WRONG, \
    YOU_JOINED_SUCCESSFUL, YOU_LEAVED_SUCCESSFUL, \
    YOU_ARE_ALREADY_JOINED, CHOOSE_SCHEDULE_TYPE, FACULTIES_ARE_EMPTY, PROGRAMS_ARE_EMPTY, START_ANSWER, \
    CHOOSE_SCHEDULE_TYPE_OR_JOIN_TO_GROUP
from consts.error import ErrorMessage
from consts.kb import ButtonText, CallbackData
from database.db import redis_client
from keyboards.reply import no_joined_kb, joined_kb
from middlewares.auth import auth_middleware
from services.group import group_service
from services.university_structure import university_structure_service
from states.group import MyGroup
from states.schedule import Schedule
from keyboards.inline import all_groups_kb, faculties_with_id_kb, programs_kb, schedule_types_kb, back_kb, \
    schedule_types_with_join_kb, my_group_kb


group_router = Router()

group_router.message.middleware(auth_middleware)
group_router.callback_query.middleware(auth_middleware)

all_groups = dict()

@group_router.message(F.text == ButtonText.GROUPS)
async def choose_faculty_handler(msg: Message, state: FSMContext):
    await state.set_state(Schedule.faculty)
    await choose_faculty_with_msg(msg, state)

async def choose_faculty_with_msg(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(name=f"chat_id:{msg.chat.id}")

        try:
            response = await university_structure_service.get_faculties(token=token)

            if "data" in response:
                if response["data"]:
                    faculties = dict()
                    for faculty in response["data"]:
                        faculties[faculty["name"]] = faculty["faculty_id"]

                    await msg.answer(text=CHOOSE_FACULTY, reply_markup=faculties_with_id_kb(faculties))
                    logging.info(msg=f"User {msg.chat.id} get faculties successful")
                else:
                    await msg.answer(text=FACULTIES_ARE_EMPTY)
                    await state.clear()
                    logging.warning(msg=f"Faculties are empty for user {msg.chat.id}")
            else:
                await msg.answer(text=FACULTIES_ARE_EMPTY)
                await state.clear()
                logging.warning(msg=f"Faculties are empty for user {msg.chat.id}")
        except Exception as e:
            logging.error(msg=f"Error when try getting faculties for user {msg.chat.id}: {e}")

    except Exception as e:
        logging.error(msg=f"Redis error when try getting chat_id:{msg.chat.id} in choose faculty: {e}")

async def choose_faculty_with_call(call: CallbackQuery, state: FSMContext):
    try:
        token = await redis_client.get(name=f"chat_id:{call.message.chat.id}")

        try:
            response = await university_structure_service.get_faculties(token=token)

            if "data" in response:
                if response["data"]:
                    faculties = dict()
                    for faculty in response["data"]:
                        faculties[faculty["name"]] = faculty["faculty_id"]

                    await call.message.edit_text(text=CHOOSE_FACULTY, reply_markup=faculties_with_id_kb(faculties))
                    logging.info(msg=f"User {call.message.chat.id} get faculties successful")
                else:
                    await call.message.edit_text(text=FACULTIES_ARE_EMPTY)
                    await state.clear()
                    logging.warning(msg=f"Faculties are empty for user {call.message.chat.id}")
            else:
                await call.message.edit_text(text=FACULTIES_ARE_EMPTY)
                await state.clear()
                logging.warning(msg=f"Faculties are empty for user {call.message.chat.id}")
        except Exception as e:
            logging.error(msg=f"Error when try getting faculties for user {call.message.chat.id}: {e}")

    except Exception as e:
        logging.error(msg=f"Redis error when try getting chat_id:{call.message.chat.id} in choose faculty: {e}")

@group_router.callback_query(F.data != CallbackData.BACK_CALLBACK, Schedule.faculty)
async def capture_faculty(call: CallbackQuery, state: FSMContext):
    await state.update_data(faculty_id=call.data)
    await chosen_faculty(call, state, call.data)

async def chosen_faculty(call: CallbackQuery, state: FSMContext, faculty_id):
    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")

        try:
            response = await university_structure_service.get_programs(token, faculty_id)

            if "data" in response:
                if response["data"]:
                    programs = list()
                    for program in response["data"]:
                        programs.append(program["name"])

                    await call.message.edit_text(text=CHOOSE_PROGRAM, reply_markup=programs_kb(programs))
                    await state.set_state(Schedule.program)
                    logging.info(msg=f"User {call.message.chat.id} get programs successful")
                else:
                    await call.message.edit_text(text=PROGRAMS_ARE_EMPTY, reply_markup=back_kb())
                    await state.set_state(Schedule.faculty)
                    logging.warning(msg=f"Programs are empty for user {call.message.chat.id}")
            else:
                await call.message.edit_text(text=PROGRAMS_ARE_EMPTY, reply_markup=back_kb())
                await state.set_state(Schedule.faculty)
                logging.warning(msg=f"Programs are empty for user {call.message.chat.id}")
        except Exception as e:
            logging.error(msg=f"Error when try getting programs for user {call.message.chat.id}: {e}")

    except Exception as e:
        logging.error(msg=f"Redis error when try getting chat_id:{call.message.chat.id} in choose program: {e}")

@group_router.callback_query(F.data == CallbackData.BACK_CALLBACK, Schedule.faculty)
async def back_faculty_handler(call: CallbackQuery, state: FSMContext):
    try:
        is_joined = await redis_client.get(f"joined:{call.message.chat.id}")

        await call.message.delete()
        await state.clear()

        if is_joined == "true":
            await call.message.answer(text=START_ANSWER, reply_markup=joined_kb())
        else:
            await call.message.answer(text=START_ANSWER, reply_markup=no_joined_kb())
    except Exception as e:
        logging.error(
            msg=f"Redis error when try getting joined:{call.message.chat.id} "\
                f"after click on back in faculties: {e}"
        )

@group_router.callback_query(F.data != CallbackData.BACK_CALLBACK, Schedule.program)
async def capture_program(call: CallbackQuery, state: FSMContext):
    await state.update_data(program=call.data)
    await chosen_program(call, state, call.data)

async def chosen_program(call: CallbackQuery, state: FSMContext, program):
    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")

        try:
            response = await group_service.get_groups(token, program)

            if "data" in response:
                if response["data"]:
                    groups = dict()
                    for group in response["data"]:
                        groups[group["short_name"]] = group["group_id"]

                    await call.message.edit_text(text=CHOOSE_GROUP, reply_markup=all_groups_kb(groups))
                    await state.set_state(Schedule.group_id)
                    logging.info(msg=f"User {call.message.chat.id} get groups successful")
                else:
                    await call.message.edit_text(text=GROUPS_WILL_BE_HERE_SOON, reply_markup=back_kb())
                    await state.set_state(Schedule.program)
                    logging.warning(msg=f"Groups are empty for user {call.message.chat.id}")
            else:
                await call.message.edit_text(text=GROUPS_WILL_BE_HERE_SOON, reply_markup=back_kb())
                await state.set_state(Schedule.program)
                logging.warning(msg=f"Groups are empty for user {call.message.chat.id}")
        except Exception as e:
            logging.error(msg=f"Error when try getting groups for user {call.message.chat.id}: {e}")

    except Exception as e:
        logging.error(msg=f"Redis error when try getting chat_id:{call.message.chat.id} in choose group: {e}")

@group_router.callback_query(F.data == CallbackData.BACK_CALLBACK, Schedule.program)
async def back_program_handler(call: CallbackQuery, state: FSMContext):
    await choose_faculty_with_call(call, state)
    await state.set_state(Schedule.faculty)

@group_router.callback_query(F.data != CallbackData.BACK_CALLBACK, Schedule.group_id)
async def capture_group(call: CallbackQuery, state: FSMContext):
    await state.update_data(group_id=call.data)
    await chosen_group(call, state, call.data)

async def chosen_group(call: CallbackQuery, state: FSMContext, group_id):
    try:
        await redis_client.set(name=f"group_id:{call.message.chat.id}", value=str(group_id))
        if await redis_client.get(name=f"joined:{call.message.chat.id}") != "true":
            await call.message.edit_text(
                text=CHOOSE_SCHEDULE_TYPE_OR_JOIN_TO_GROUP,
                reply_markup=schedule_types_with_join_kb()
            )
        else:
            await call.message.edit_text(
                text=CHOOSE_SCHEDULE_TYPE,
                reply_markup=schedule_types_kb()
            )
        await state.set_state(Schedule.schedule_type)
    except Exception as e:
        logging.error(msg=f"Redis error when try choose group for user {call.message.chat.id}: {e}")

@group_router.callback_query(F.data == CallbackData.BACK_CALLBACK, Schedule.group_id)
async def back_group_handler(call: CallbackQuery, state: FSMContext):
    faculty_id = await state.get_value("faculty_id")
    await chosen_faculty(call, state, faculty_id)

@group_router.callback_query(F.data == CallbackData.BACK_CALLBACK, Schedule.schedule_type)
async def back_schedule_handler(call: CallbackQuery, state: FSMContext):
    try:
        my_group_id = await redis_client.get(f"my_group_id:{call.message.chat.id}")
        if my_group_id:
            group_id = await redis_client.get(f"group_id:{call.message.chat.id}")
            if my_group_id != group_id:
                await redis_client.set(name=f"group_id:{call.message.chat.id}", value=str(my_group_id))
            else:
                await call.message.delete()
                await call.message.answer(text=START_ANSWER, reply_markup=joined_kb())
                return

            program = await state.get_value("program")
            await chosen_program(call, state, program)
        else:
            if await redis_client.get(f"joined:{call.message.chat.id}") == "true":
                await call.message.delete()
                await call.message.answer(text=START_ANSWER, reply_markup=joined_kb())
            else:
                program = await state.get_value("program")
                await chosen_program(call, state, program)
    except Exception as e:
        logging.error(msg=f"Redis error when try back schedule for user {call.message.chat.id}: {e}")

@group_router.callback_query(F.data == CallbackData.JOIN_CALLBACK)
async def group_join_handler(call: CallbackQuery, state: FSMContext):
    try:
        group_id = await state.get_value("group_id")
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")

        try:
            response = await group_service.join(token=token, group_id=group_id)

            if "data" in response:
                if "error" in response["data"]:
                    match response["data"]["error"]:
                        case ErrorMessage.YOU_ARE_ALREADY_IN_GROUP:
                            await redis_client.set(name=f"joined:{call.message.chat.id}", value="true")
                            await call.message.delete()
                            await call.message.answer(text=YOU_ARE_ALREADY_JOINED, reply_markup=joined_kb())
                    await state.clear()
                    return
        except Exception as e:
            logging.error(msg=f"Error when user {call.message.chat.id} try to join to group_id={group_id}: {e}")

        await redis_client.set(name=f"joined:{call.message.chat.id}", value="true")
        await call.message.delete()
        await call.message.answer(text=YOU_JOINED_SUCCESSFUL, reply_markup=joined_kb())
        logging.info(msg=f"User {call.message.chat.id} joined to group_id={group_id} successful")
    except Exception as e:
        logging.error(msg=f"Redis error when try join to group for user {call.message.chat.id}: {e}")

@group_router.message(F.text == ButtonText.MY_GROUP)
async def my_group_handler(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")

        try:
            response = await group_service.get_my(token)

            if "data" in response:
                if "group_id" in response["data"]:
                    await redis_client.set(name=f"group_id:{msg.chat.id}", value=str(response["data"]["group_id"]))
                    await redis_client.set(name=f"my_group_id:{msg.chat.id}", value=str(response["data"]["group_id"]))
                    if await redis_client.get(f"joined:{msg.chat.id}") != "true":
                        await redis_client.set(name=f"joined:{msg.chat.id}", value="true")
                    answer = group_service.get_info(response["data"])
                    await msg.answer(text=answer, reply_markup=my_group_kb())
                    await state.set_state(MyGroup.group)
                    logging.info(msg=f"User {msg.chat.id} get group info successful")
                else:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=joined_kb())
                    logging.warning(msg=f"Error when try getting group info for user {msg.chat.id}")
        except Exception as e:
            logging.error(msg=f"Error when try getting group info for user {msg.chat.id}: {e}")

    except Exception as e:
        logging.error(msg=f"Redis error when try getting chat_id:{msg.chat.id} in get group info: {e}")

@group_router.callback_query(F.data == CallbackData.BACK_CALLBACK, MyGroup.group)
async def back_my_group_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text=START_ANSWER, reply_markup=joined_kb())
    await state.clear()

@group_router.callback_query(F.data == CallbackData.LEAVE_CALLBACK)
async def leave_group_handler(call: CallbackQuery, state: FSMContext):
    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")

        try:
            response = await group_service.leave(token)

            if "data" in response:
                if "error" not in response["data"]:
                    await call.message.delete()
                    await call.message.answer(text=YOU_LEAVED_SUCCESSFUL, reply_markup=no_joined_kb())
                    logging.info(msg=f"User {call.message.chat.id} leave from group successful")
                else:
                    await call.message.delete()
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=joined_kb())
                    logging.warning(msg=f"Error when try to leaving from group for user {call.message.chat.id}")
                    return
        except Exception as e:
            logging.error(msg=f"Error when try to leaving from group for user {call.message.chat.id}: {e}")

        await redis_client.delete(f"joined:{call.message.chat.id}")
        await redis_client.delete(f"group_id:{call.message.chat.id}")
        await redis_client.delete(f"my_group_id:{call.message.chat.id}")
        await state.clear()
    except Exception as e:
        logging.error(msg=f"Redis error when try leaving from group for user {call.message.chat.id}: {e}")

@group_router.message(F.text == ButtonText.ANOTHER_GROUP_SCHEDULE)
async def another_group_schedule_handler(msg: Message, state: FSMContext):
    try:
        group_id = await redis_client.get(name=f"group_id:{msg.chat.id}")
        await redis_client.set(name=f"my_group_id:{msg.chat.id}", value=str(group_id))

        await state.set_state(Schedule.faculty)
        await choose_faculty_with_msg(msg, state)
    except Exception as e:
        logging.error(msg=f"Redis error when try getting group_id:{msg.chat.id} in another group schedule: {e}")
