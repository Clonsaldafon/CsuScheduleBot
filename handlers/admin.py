from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from consts.bot_answer import SOMETHING_WENT_WRONG, CHOOSE_FACULTY, CHOOSE_PROGRAM, ENTER_SHORT_GROUP_NAME, \
    IN_DEVELOPING, SOMETHING_WITH_MY_MEMORY, CHOOSE_YOUR_ROLE_AGAIN, GROUP_WITH_THIS_SHORT_NAME_ALREADY_EXISTS
from consts.error import ErrorMessage
from consts.kb import ButtonText, CallbackData
from database.db import redis_client
from keyboards.inline import faculties_with_id_kb, programs_with_id_kb, roles_kb
from keyboards.reply import admin_kb
from services.admin import AdminService
from services.university_structure import UniversityStructureService
from states.group import Group
from states.university_structure import UniversityStructure

admin_router = Router()
admin_service = AdminService()
university_structure_service = UniversityStructureService()

@admin_router.message(F.text == ButtonText.CREATE_GROUP)
async def create_group_handler(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        response = await university_structure_service.get_faculties(token)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=admin_kb())
            await state.clear()
        else:
            faculties = dict()
            for faculty in response["data"]:
                faculties[faculty["name"]] = faculty["faculty_id"]

            await msg.answer(text=CHOOSE_FACULTY, reply_markup=faculties_with_id_kb(faculties))
            await state.set_state(UniversityStructure.faculty_id)
    except Exception as e:
        print(e)

@admin_router.callback_query(F.data != CallbackData.BACK_CALLBACK, UniversityStructure.faculty_id)
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
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=admin_kb())
            await state.clear()
        else:
            programs = dict()
            for program in response["data"]:
                programs[program["name"]] = program["program_id"]

            await call.message.edit_text(text=CHOOSE_PROGRAM, reply_markup=programs_with_id_kb(programs))
            await state.set_state(UniversityStructure.program_id)
    except Exception as e:
        print(e)

@admin_router.callback_query(F.data != CallbackData.BACK_CALLBACK, UniversityStructure.program_id)
async def capture_program(call: CallbackQuery, state: FSMContext):
    await state.update_data(program_id=call.data)
    await call.message.answer(text=ENTER_SHORT_GROUP_NAME, reply_markup=None)
    await state.set_state(UniversityStructure.short_name)

@admin_router.callback_query(F.data == CallbackData.BACK_CALLBACK, UniversityStructure.program_id)
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
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=admin_kb())
            await state.clear()
        else:
            faculties = dict()
            for faculty in response["data"]:
                faculties[faculty["name"]] = faculty["faculty_id"]

            await call.message.edit_text(text=CHOOSE_FACULTY, reply_markup=faculties_with_id_kb(faculties))
            await state.set_state(UniversityStructure.faculty_id)
    except Exception as e:
        print(e)

@admin_router.message(F.text, UniversityStructure.short_name)
async def capture_short_name(msg: Message, state: FSMContext):
    short_name = msg.text
    await state.update_data(short_name=short_name)

    data = await state.get_data()

    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        response = await admin_service.create_group(
            token=token,
            faculty_id=int(data.get("faculty_id")),
            program_id=int(data.get("program_id")),
            short_name=data.get("short_name")
        )

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case ErrorMessage.GROUP_ALREADY_EXISTS:
                    await msg.answer(text=GROUP_WITH_THIS_SHORT_NAME_ALREADY_EXISTS, reply_markup=None)
                    await state.set_state(UniversityStructure.short_name)
                case _:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=admin_kb())
            await state.clear()
        else:
            await msg.answer(text=f"Группа {short_name} успешно создана!", reply_markup=admin_kb())
            await state.clear()
    except Exception as e:
        print(e)

@admin_router.callback_query(F.data == CallbackData.BACK_CALLBACK, UniversityStructure.short_name)
async def back_short_name_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        response = await university_structure_service.get_programs(token, data.get("faculty_id"))

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await call.message.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await call.message.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=admin_kb())
            await state.clear()
        else:
            programs = dict()
            for program in response["data"]:
                programs[program["name"]] = program["program_id"]

            await call.message.edit_text(text=CHOOSE_PROGRAM, reply_markup=programs_with_id_kb(programs))
            await state.set_state(UniversityStructure.program_id)
    except Exception as e:
        print(e)

@admin_router.message(F.text == ButtonText.EDIT_SCHEDULE)
async def edit_schedule_handler(msg: Message):
    await msg.answer(text=IN_DEVELOPING, reply_markup=admin_kb())
