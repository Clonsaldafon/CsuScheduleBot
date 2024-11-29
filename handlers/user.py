from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import redis_client
from keyboards.inline import auth_kb
from keyboards.reply import to_start_kb, no_subscribed_kb, choose_faculty_kb
from services.user import UserService
from states.user import LogIn, SignUp


user_router = Router()
user_service = UserService()

@user_router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(
        text="Привет 👋\n" +
             "Давай знакомиться, для этого создай новый аккаунт либо войди в существующий ⤵",
        reply_markup=auth_kb()
    )

@user_router.callback_query(F.data.in_({"login", "signup"}))
async def auth_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    data = call.data
    match data:
        case "login":
            await call.message.answer(
                text="Хм... Я тебя не помню 🤔\n" +
                     "Напиши свой email 📧",
                reply_markup=to_start_kb()
            )
            await state.set_state(LogIn.email)
        case "signup":
            await call.message.answer(
                text="Я рад, что смог заинтересовать тебя 🤗\n" +
                     "Заполнишь небольшую анкету? Это займет немного времени ⏰\n" +
                     "Но зато я тебя запомню, для начала напиши свой email 📧",
                reply_markup=to_start_kb()
            )
            await state.set_state(SignUp.email)

@user_router.message(F.text == "В начало 🔙")
async def to_start_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        text="Создай новый аккаунт либо войди в существующий ⤵",
        reply_markup=auth_kb()
    )

@user_router.message(F.text, LogIn.email)
async def capture_email_auth(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(
        text="Как-будто что-то знакомое... 🤔\n" +
             "А какой пароль? 🔒",
        reply_markup=to_start_kb()
    )
    await state.set_state(LogIn.password)

@user_router.message(F.text, LogIn.password)
async def capture_password_auth(msg: Message, state: FSMContext):
    await state.update_data(password=msg.text)
    await msg.delete()
    data = await state.get_data()

    try:
        response = await user_service.log_in(
           email=data.get("email"),
           password=data.get("password")
        )

        if "access_token" in response:
            await redis_client.set(
                name=f"tg_id:{msg.from_user.id}",
                value=str(response["access_token"])
            )
            await state.clear()

            is_group_id_exists = await redis_client.exists(f"group_id:{msg.from_user.id}")
            if is_group_id_exists:
                await msg.answer(
                    text="Теперь вспомнил 🤪\n" +
                         "Как же я мог тебя забыть 🤦‍♂️",
                    reply_markup=no_subscribed_kb()
                )
            else:
                await msg.answer(
                    text="Теперь вспомнил 🤪\n" +
                         "Как же я мог тебя забыть 🤦‍♂️",
                    reply_markup=choose_faculty_kb()
                )
        else:
            match response["error"]:
                case "user not found":
                    await msg.answer(
                        text="Никак не могу вспомнить человека с таким email 😔\n" +
                             "Попробуй использовать другой адрес",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(LogIn.email)
                case "Key: 'LogInRequest.Email' Error:Field validation for 'Email' failed on the 'email' tag":
                    await msg.answer(
                        text="Неверный формат email 🧐\n" +
                             "Попробуй еще раз",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(LogIn.email)
                case "wrong password":
                    await msg.answer(
                        text="Неверный пароль 🔒\n" +
                             "Попробуй ввести его еще раз",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(LogIn.password)
                case _:
                    await msg.answer(
                        text="Похоже, что-то пошло не по плану... 🫣\n" +
                             "Попробуй ввести email еще раз ✍",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(LogIn.email)
    except Exception as e:
        print(e)

@user_router.message(F.text, SignUp.email)
async def capture_email(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(
        text="Придумай сложный пароль (не менее 8 символов) 🔒",
        reply_markup=to_start_kb()
    )
    await state.set_state(SignUp.password)

@user_router.message(F.text, SignUp.password)
async def capture_password(msg: Message, state: FSMContext):
    if 8 <= len(msg.text) <= 40:
        await state.update_data(password=msg.text)
        await msg.delete()
        await msg.answer(
            text="Я уверен, что у того, кто захочет взломать твой аккаунт, не будет столько свободного времени 🤓\n"
                 "И наконец, финальный вопрос: как тебя зовут? Напиши ФИО ✍",
            reply_markup=to_start_kb()
        )
        await state.set_state(SignUp.fullName)
    else:
        await msg.delete()
        await msg.answer(
            text="Этот пароль легко взломает даже пятиклассник 🤪\n" +
                 "Придумай что-то посложнее",
            reply_markup=to_start_kb()
        )
        await state.set_state(SignUp.password)

@user_router.message(F.text, SignUp.fullName)
async def capture_fullname(msg: Message, state: FSMContext):
    await state.update_data(fullName=msg.text)
    data = await state.get_data()

    try:
        response = await user_service.sign_up(
            email=data.get("email"),
            password=data.get("password"),
            full_name=data.get("fullName"),
            telegram=str(msg.from_user.id)
        )

        if "access_token" in response:
            await redis_client.set(
                name=f"tg_id:{msg.from_user.id}",
                value=str(response["access_token"])
            )
            await msg.answer(
                text="Теперь-то будем знакомы! 😊",
                reply_markup=choose_faculty_kb()
            )
            await state.clear()
        else:
            match response["error"]:
                case "user already exists":
                    await msg.answer(
                        text="Я уже знаком с человеком, у которого такой же email 🤨\n" +
                             "Попробуй использовать другой адрес",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(SignUp.email)
                case "Key: 'SignUpRequest.Email' Error:Field validation for 'Email' failed on the 'email' tag":
                    await msg.answer(
                        text="Неверный формат email 🧐\n" +
                             "Попробуй еще раз",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(SignUp.email)
                case "Key: 'SignUpRequest.Password' Error:Field validation for 'Password' failed on the 'min' tag":
                    await msg.answer(
                        text="Пароль слишком простой 🙃\n" +
                             "Придумай другой",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(SignUp.password)
                case _:
                    await msg.answer(
                        text="Похоже, что-то пошло не по плану... 🫣\n" +
                             "Попробуй ввести email еще раз ✍",
                        reply_markup=to_start_kb()
                    )
                    await state.set_state(SignUp.email)
    except Exception as e:
        print(e)
