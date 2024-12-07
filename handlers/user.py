import re
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from consts.bot_answer import START_COMMAND, START_ANSWER, STUDENT_SIGN_UP, STUDENT_SIGNED_UP, \
    SOMETHING_WITH_FULLNAME_VALIDATION, STUDENT_IS_ALREADY_SIGNED_UP, STUDENT_NO_SIGNED_UP, SOMETHING_WENT_WRONG, \
    ADMIN_START, ENTER_YOUR_EMAIL, INVENT_PASSWORD, ADMIN_SIGNED_UP_SUCCESS, ADMIN_EMAIL_VALIDATION, \
    ADMIN_WITH_THIS_EMAIL_ALREADY_EXISTS, ADMIN_PASSWORD_IS_SHORT, ENTER_PASSWORD, ADMIN_LOGGED_IN_SUCCESS, \
    ADMIN_WITH_THIS_EMAIL_NO_EXISTS, WRONG_PASSWORD, STUDENT_LOGGED_IN, CHOOSE_YOUR_ROLE_AGAIN, FEEDBACK_LATER, \
    HELP_COMMAND, HELP_ANSWER
from consts.error import ErrorMessage
from consts.kb import ButtonText, CallbackData
from database.db import redis_client
from keyboards.inline import auth_kb, roles_kb
from keyboards.reply import to_start_kb, choose_faculty_kb, admin_kb, joined_kb, no_joined_kb
from services.user import UserService
from states.admin import AdminSignUp, AdminLogIn
from states.student import StudentSignUp, StudentLogIn

user_router = Router()
user_service = UserService()

@user_router.message(Command(START_COMMAND))
async def start_handler(msg: Message):
    await redis_client.set(name=f"started_at:{msg.chat.id}", value=str(datetime.now()))

    await msg.answer(text=START_ANSWER, reply_markup=roles_kb())

@user_router.message(Command(HELP_COMMAND))
async def help_handler(msg: Message):
    await msg.answer(text=HELP_ANSWER)

@user_router.callback_query(F.data == CallbackData.STUDENT_CALLBACK)
async def student_handler(call: CallbackQuery, state: FSMContext):
    try:
        response = await user_service.log_in_student(call.message.chat.id)

        if "access_token" in response["data"]:
            await redis_client.set(name=f"chat_id:{call.message.chat.id}", value=str(response["data"]["access_token"]))

            is_joined = await redis_client.get(f"joined:{call.message.chat.id}")
            if is_joined is None:
                await call.message.answer(text=STUDENT_LOGGED_IN, reply_markup=choose_faculty_kb())
                await state.clear()
                return

            kb = joined_kb if (is_joined == "true") else no_joined_kb
            await call.message.answer(text=STUDENT_LOGGED_IN, reply_markup=kb())
            await state.clear()
        else:
            await call.message.answer(text=STUDENT_SIGN_UP, reply_markup=None)
            await state.set_state(StudentSignUp.fullname)
    except Exception as e:
        print(e)

@user_router.message(F.text, StudentSignUp.fullname)
async def capture_student_fullname_signup(msg: Message, state: FSMContext):
    fullname = msg.text
    telegram = msg.chat.id
    username = msg.chat.username
    await state.update_data(fullname=fullname)

    try:
        if is_fullname_valid(fullname):
            response = await user_service.sign_up_student(fullname=fullname, telegram=telegram, username=username)
            if response["status_code"] == 201:
                await redis_client.set(name=f"chat_id:{msg.chat.id}", value=str(response["data"]["access_token"]))
                await msg.answer(text=STUDENT_SIGNED_UP, reply_markup=choose_faculty_kb())
                await state.clear()
            else:
                match response["data"]["error"]:
                    case ErrorMessage.SIGN_UP_FULLNAME_VALIDATION:
                        await msg.answer(text=SOMETHING_WITH_FULLNAME_VALIDATION, reply_markup=None)
                        await state.set_state(StudentSignUp.fullname)
                    case ErrorMessage.USER_ALREADY_EXISTS:
                        login_response = await user_service.log_in_student(telegram=telegram)
                        if login_response["status_code"] == 200:
                            await msg.answer(text=STUDENT_IS_ALREADY_SIGNED_UP, reply_markup=choose_faculty_kb())
                            await state.clear()
                        else:
                            match login_response["data"]["error"]:
                                case ErrorMessage.USER_NOT_FOUND:
                                    await msg.answer(text=STUDENT_NO_SIGNED_UP, reply_markup=None)
                                    await state.set_state(StudentSignUp.fullname)
                    case _:
                        await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=ReplyKeyboardRemove())
                        await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                        await state.clear()
        else:
            await msg.answer(text=SOMETHING_WITH_FULLNAME_VALIDATION, reply_markup=None)
            await state.set_state(StudentSignUp.fullname)
    except Exception as e:
        print(e)

def is_fullname_valid(fullname: str) -> bool:
    pattern = r'^(?:[А-ЯЁ][а-яё]+[-\s]?)*[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+$'
    if re.match(pattern, fullname):
        return True
    return False

@user_router.message(F.text, StudentLogIn.fullname)
async def capture_student_fullname_login(msg: Message, state: FSMContext):
    # TODO: make student authorization
    pass

@user_router.callback_query(F.data == CallbackData.ADMIN_CALLBACK)
async def admin_handler(call: CallbackQuery, state: FSMContext):
    # await call.message.edit_text(text=ADMIN_START, reply_markup=auth_kb())
    await call.message.answer(text="🤖 Куда собрался?🤨\nТебе сюда нелья! Заходи, как студент")
    try:
        response = await user_service.log_in_student(call.message.chat.id)

        if "access_token" in response["data"]:
            await redis_client.set(name=f"chat_id:{call.message.chat.id}", value=str(response["data"]["access_token"]))

            is_joined = await redis_client.get(f"joined:{call.message.chat.id}")
            if is_joined is None:
                await call.message.answer(text=STUDENT_LOGGED_IN, reply_markup=choose_faculty_kb())
                await state.clear()
                return

            kb = joined_kb if (is_joined == "true") else no_joined_kb
            await call.message.answer(text=STUDENT_LOGGED_IN, reply_markup=kb())
            await state.clear()
        else:
            await call.message.answer(text=STUDENT_SIGN_UP, reply_markup=None)
            await state.set_state(StudentSignUp.fullname)
    except Exception as e:
        print(e)

@user_router.callback_query(F.data.in_({CallbackData.LOG_IN_CALLBACK, CallbackData.SIGN_UP_CALLBACK}))
async def admin_auth_handler(call: CallbackQuery, state: FSMContext):
    match call.data:
        case CallbackData.LOG_IN_CALLBACK:
            await call.message.answer(text=ENTER_YOUR_EMAIL, reply_markup=to_start_kb())
            await state.set_state(AdminLogIn.email)
        case CallbackData.SIGN_UP_CALLBACK:
            await call.message.answer(text=ENTER_YOUR_EMAIL, reply_markup=to_start_kb())
            await state.set_state(AdminSignUp.email)

@user_router.message(F.text == ButtonText.TO_START)
async def to_start_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(text=ADMIN_START, reply_markup=auth_kb())

@user_router.message(F.text, AdminSignUp.email)
async def capture_admin_email_signup(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(text=INVENT_PASSWORD, reply_markup=to_start_kb())
    await state.set_state(AdminSignUp.password)

@user_router.message(F.text, AdminSignUp.password)
async def capture_admin_password_signup(msg: Message, state: FSMContext):
    if 8 <= len(msg.text) <= 40:
        await state.update_data(password=msg.text)
        await msg.delete()
        data = await state.get_data()

        try:
            response = await user_service.sign_up_admin(email=data.get("email"),password=data.get("password"))
            if response["status_code"] == 201:
                await redis_client.set(name=f"chat_id:{msg.chat.id}", value=str(response["data"]["access_token"]))
                await msg.answer(text=ADMIN_SIGNED_UP_SUCCESS, reply_markup=admin_kb())
                await state.clear()
            else:
                match response["data"]["error"]:
                    case ErrorMessage.SIGN_UP_EMAIL_VALIDATION:
                        await msg.answer(text=ADMIN_EMAIL_VALIDATION, reply_markup=to_start_kb())
                        await state.set_state(AdminSignUp.email)
                    case ErrorMessage.USER_ALREADY_EXISTS:
                        await msg.answer(text=ADMIN_WITH_THIS_EMAIL_ALREADY_EXISTS, reply_markup=to_start_kb())
                        await state.set_state(AdminSignUp.email)
                    case _:
                        await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=ReplyKeyboardRemove())
                        await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                        await state.clear()
        except Exception as e:
            print(e)
    else:
        await msg.delete()
        await msg.answer(text=ADMIN_PASSWORD_IS_SHORT, reply_markup=to_start_kb())
        await state.set_state(AdminSignUp.password)

@user_router.message(F.text, AdminLogIn.email)
async def capture_admin_email_login(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(text=ENTER_PASSWORD, reply_markup=to_start_kb())
    await state.set_state(AdminLogIn.password)

@user_router.message(F.text, AdminLogIn.password)
async def capture_admin_password_login(msg: Message, state: FSMContext):
    await state.update_data(password=msg.text)
    await msg.delete()
    data = await state.get_data()

    try:
        response = await user_service.log_in_admin(email=data.get("email"), password=data.get("password"))
        if response["status_code"] == 200:
            await redis_client.set(name=f"chat_id:{msg.chat.id}", value=str(response["access_token"]))
            await msg.answer(text=ADMIN_LOGGED_IN_SUCCESS, reply_markup=admin_kb())
            await state.clear()
        else:
            match response["data"]["error"]:
                case ErrorMessage.LOG_IN_EMAIL_VALIDATION:
                    await msg.answer(text=ADMIN_EMAIL_VALIDATION, reply_markup=to_start_kb())
                    await state.set_state(AdminLogIn.email)
                case ErrorMessage.USER_NOT_FOUND:
                    await msg.answer(text=ADMIN_WITH_THIS_EMAIL_NO_EXISTS, reply_markup=to_start_kb())
                    await state.set_state(AdminLogIn.email)
                case ErrorMessage.WRONG_PASSWORD:
                    await msg.answer(text=WRONG_PASSWORD, reply_markup=to_start_kb())
                    await state.set_state(AdminLogIn.password)
                case _:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=ReplyKeyboardRemove())
                    await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                    await state.clear()
    except Exception as e:
        print(e)

@user_router.callback_query(F.data == CallbackData.FEEDBACK_LATER_CALLBACK)
async def feedback_rejection_handler(call: CallbackQuery):
    await redis_client.set(name=f"started_at:{call.message.chat.id}", value=str(datetime.now()))

    await call.message.answer(text=FEEDBACK_LATER, reply_markup=None)