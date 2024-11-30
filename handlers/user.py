from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import redis_client
from keyboards.inline import auth_kb, roles_kb
from keyboards.reply import to_start_kb, no_subscribed_kb, choose_faculty_kb, admin_kb
from services.user import UserService
from states.admin import AdminSignUp, AdminLogIn
from states.student import StudentSignUp, StudentLogIn

user_router = Router()
user_service = UserService()

@user_router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(
        text="Привет 👋\n" +
             "Чтобы мы с тобой могли взаимодействовать друг с другом, тебе нужно выбрать свою роль ⤵",
        reply_markup=roles_kb()
    )

@user_router.callback_query(F.data == "student")
async def student_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Давай знакомиться! Как тебя зовут? Напиши ФИО ✍️", reply_markup=None)
    await state.set_state(StudentSignUp.fullname)

@user_router.message(F.text, StudentSignUp.fullname)
async def capture_student_fullname_signup(msg: Message, state: FSMContext):
    fullname = msg.text
    telegram = msg.chat.id
    await state.update_data(fullname=fullname)

    try:
        response = await user_service.sign_up_student(fullname=fullname, telegram=telegram)
        if response["status_code"] == 201:
            await redis_client.set(name=f"chat_id:{msg.chat.id}", value=str(response["data"]["access_token"]))
            await msg.answer(text="Теперь-то будем знакомы! 😊", reply_markup=choose_faculty_kb())
            await state.clear()
        else:
            match response["data"]["error"]:
                case ("Key: 'SignUpWithTelegramRequest.Fullname' Error:Field validation "
                      "for 'Fullname' failed on the 'required' tag"):
                    await msg.answer(text="Что-то не так с ФИО... Попробуй ввести еще раз", reply_markup=None)
                    await state.set_state(StudentSignUp.fullname)
                case "user already exists":
                    login_response = await user_service.log_in_student(telegram=telegram)
                    if login_response["status_code"] == 200:
                        await msg.answer(text="Мы ведь уже знакомились однажды 🤨", reply_markup=choose_faculty_kb())
                        await state.clear()
                    else:
                        match login_response["data"]["error"]:
                            case "user not found":
                                await msg.answer(text="Я тебя не знаю 🫣\nВведи ФИО еще раз", reply_markup=None)
                                await state.set_state(StudentSignUp.fullname)
                case _:
                    await msg.answer(text="🤖 Что-то пошло не так... Попробуйте позже ", reply_markup=roles_kb())
                    await state.clear()
    except Exception as e:
        print(e)

@user_router.message(F.text, StudentLogIn.fullname)
async def capture_student_fullname_signup(msg: Message, state: FSMContext):
    # TODO: make student authorization
    pass

@user_router.callback_query(F.data == "admin")
async def admin_handler(call: CallbackQuery):
    await call.message.edit_text(
        text="Для начала работы Вам нужно создать аккаунт или войти в существующий ⤵",
        reply_markup=auth_kb()
    )

@user_router.callback_query(F.data.in_({"login", "signup"}))
async def admin_auth_handler(call: CallbackQuery, state: FSMContext):
    data = call.data
    match data:
        case "login":
            await call.message.answer(
                text="Введите свой email 📧",
                reply_markup=to_start_kb()
            )
            await state.set_state(AdminLogIn.email)
        case "signup":
            await call.message.answer(
                text="Введите свой email 📧",
                reply_markup=to_start_kb()
            )
            await state.set_state(AdminSignUp.email)

@user_router.message(F.text == "В начало 🔙")
async def to_start_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        text="Для начала работы Вам нужно создать аккаунт или войти в существующий ⤵",
        reply_markup=auth_kb()
    )

@user_router.message(F.text, AdminSignUp.email)
async def capture_admin_email_signup(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(
        text="Придумайте сложный пароль (не менее 8 символов) 🔒",
        reply_markup=to_start_kb()
    )
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
                await msg.answer(text="Вы успешно зарегистрировались!", reply_markup=admin_kb())
                await state.clear()
            else:
                match response["data"]["error"]:
                    case "Key: 'SignUpRequest.Email' Error:Field validation for 'Email' failed on the 'email' tag":
                        await msg.answer(
                            text="Неверный формат email. Попробуйте ввести его еще раз",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(AdminSignUp.email)
                    case "user already exists":
                        await msg.answer(
                            text="Пользователь с таким email уже существует. Введите другой",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(AdminSignUp.email)
                    case _:
                        await msg.answer(text="🤖 Что-то пошло не так... Попробуйте позже ", reply_markup=roles_kb())
                        await state.clear()
        except Exception as e:
            print(e)
    else:
        await msg.delete()
        await msg.answer(
            text="Этот пароль слишком простой, придумайте другой",
            reply_markup=to_start_kb()
        )
        await state.set_state(AdminSignUp.password)

@user_router.message(F.text, AdminLogIn.email)
async def capture_admin_email_login(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(text="Введите пароль 🔒", reply_markup=to_start_kb())
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
            await msg.answer(text="Вы вошли в систему!", reply_markup=admin_kb())
            await state.clear()
        else:
            match response["data"]["error"]:
                case "Key: 'SignUpRequest.Email' Error:Field validation for 'Email' failed on the 'email' tag":
                    await msg.answer(
                        text="Неверный формат email. Попробуйте ввести его еще раз",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(AdminLogIn.email)
                case "user not found":
                    await msg.answer(
                        text="Пользователя с таким email не существует. Введите другой или зарегистрируйтесь",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(AdminLogIn.email)
                case "wrong password":
                    await msg.answer(text="Неверный пароль! Попробуйте ввести еще раз", reply_markup=to_start_kb())
                    await state.set_state(AdminLogIn.password)
                case _:
                    await msg.answer(text="🤖 Что-то пошло не так... Попробуйте позже ", reply_markup=roles_kb())
                    await state.clear()
    except Exception as e:
        print(e)
