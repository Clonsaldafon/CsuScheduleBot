from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from consts.bot_answer import SOMETHING_WITH_MY_MEMORY, DATA_UPDATED_SUCCESSFUL, ENTER_NEW_FULL_NAME, CHOOSE_SETTINGS, \
    CHOOSE_NOTIFICATION_DELAY, SOMETHING_WENT_WRONG, CHOOSE_YOUR_ROLE_AGAIN, SOMETHING_WITH_FULLNAME_VALIDATION, \
    YOU_NEED_TO_USE_BUTTONS
from consts.error import ErrorMessage
from consts.kb import ButtonText, CallbackData
from database.db import redis_client
from handlers.user import is_fullname_valid
from keyboards.inline import profile_kb, notifications_kb, notification_delay_kb, roles_kb, back_kb
from keyboards.reply import joined_kb, no_joined_kb
from services.student import StudentService
from services.user import UserService
from states.student import StudentEditProfile

student_router = Router()
user_service = UserService()
student_service = StudentService()

is_notifications_enabled = False

student_info = ""
is_joined = ""

@student_router.message(F.text == ButtonText.MY_PROFILE)
async def my_profile_handler(msg: Message, state: FSMContext):
    await state.set_state(StudentEditProfile.profile)

    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        global is_joined
        is_joined = await redis_client.get(f"joined:{msg.chat.id}")
        response = await user_service.who(token)

        if "error" in response["data"]:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=profile_kb(is_joined))
        else:
            global is_notifications_enabled
            is_notifications_enabled = response["data"]["notifications_enabled"]

            answer = f"<i>{"Студент" if response["data"]["role"] == "student" else "Староста"}</i>\n"
            answer += f"<b>ФИО:</b> {response["data"]["full_name"]}\n"
            answer += f"<b>Имя пользователя:</b> @{response["data"]["telegram_username"]}\n"
            answer += f"<b>Уведомления:</b> {"включены" if is_notifications_enabled else "отключены"}\n"
            if is_notifications_enabled:
                answer += f"Уведомлять за <b>{response["data"]["notification_delay"]} мин.</b> до пары"

            global student_info
            student_info = answer
            await msg.answer(text=answer, reply_markup=profile_kb(is_joined))
    except Exception as e:
        print(e)

@student_router.callback_query(F.data == CallbackData.BACK_CALLBACK, StudentEditProfile.profile)
async def back_my_profile_handler(call: CallbackQuery, state: FSMContext):
    kb = joined_kb if (is_joined == "true") else no_joined_kb
    await call.message.delete()
    await call.message.answer(text=YOU_NEED_TO_USE_BUTTONS, reply_markup=kb())
    await state.clear()

@student_router.callback_query(F.data == CallbackData.EDIT_FULL_NAME_CALLBACK)
async def edit_full_name_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text=ENTER_NEW_FULL_NAME, reply_markup=back_kb())
    await state.set_state(StudentEditProfile.fullname)

@student_router.message(F.text, StudentEditProfile.fullname)
async def capture_new_full_name(msg: Message, state: FSMContext):
    full_name = msg.text
    await state.update_data(fullname=full_name)

    try:
        if is_fullname_valid(full_name):
            token = await redis_client.get(f"chat_id:{msg.chat.id}")
            global is_joined
            is_joined = await redis_client.get(f"joined:{msg.chat.id}")
            kb = joined_kb if (is_joined == "true") else no_joined_kb

            response = await student_service.update_full_name(token, full_name)

            if response["status_code"] == 200:
                await msg.answer(text=DATA_UPDATED_SUCCESSFUL, reply_markup=kb())
                await state.clear()
            else:
                match response["data"]["error"]:
                    case ErrorMessage.TOKEN_IS_EXPIRED:
                        await msg.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                        await msg.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                    case _:
                        await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=None)
        else:
            await msg.answer(text=SOMETHING_WITH_FULLNAME_VALIDATION, reply_markup=back_kb())
            await state.set_state(StudentEditProfile.fullname)
    except Exception as e:
        print(e)

@student_router.callback_query(F.data == CallbackData.BACK_CALLBACK, StudentEditProfile.fullname)
async def back_new_full_name_handler(call: Message, state: FSMContext):
    await call.message.edit_text(text=student_info, reply_markup=profile_kb(is_joined))
    await state.set_state(StudentEditProfile.profile)

@student_router.callback_query(F.data == CallbackData.EDIT_NOTIFICATIONS_CALLBACK)
async def edit_notifications_handler(call: CallbackQuery):
    await call.message.edit_text(text=CHOOSE_SETTINGS, reply_markup=notifications_kb(is_notifications_enabled))

@student_router.callback_query(F.data.in_({
    CallbackData.ENABLE_NOTIFICATIONS_CALLBACK,
    CallbackData.DISABLE_NOTIFICATIONS_CALLBACK
}))
async def capture_notifications_enabling(call: CallbackQuery):
    enabled = call.data == CallbackData.ENABLE_NOTIFICATIONS_CALLBACK

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        global is_joined
        is_joined = await redis_client.get(f"joined:{call.message.chat.id}")
        kb = joined_kb if (is_joined == "true") else no_joined_kb

        response = await student_service.update_notifications_enabled(token, enabled)

        if response["status_code"] == 200:
            if enabled:
                await call.message.edit_text(text=CHOOSE_NOTIFICATION_DELAY, reply_markup=notification_delay_kb())
            else:
                await call.message.answer(text=DATA_UPDATED_SUCCESSFUL, reply_markup=kb())
        else:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await call.message.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await call.message.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=None)
    except Exception as e:
        print(e)

@student_router.callback_query(F.data == CallbackData.NOTIFICATIONS_DELAY_CALLBACK)
async def edit_notification_delay_handler(call: CallbackQuery):
    await call.message.edit_text(text=CHOOSE_NOTIFICATION_DELAY, reply_markup=notification_delay_kb())

@student_router.callback_query(F.data.in_({
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_5",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_10",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_20",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_30",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_45",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_60",
}))
async def capture_edit_notification_delay(call: CallbackQuery):
    delay = int(call.data.split("_")[-1])

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        global is_joined
        is_joined = await redis_client.get(f"joined:{call.message.chat.id}")
        kb = joined_kb if (is_joined == "true") else no_joined_kb

        response = await student_service.update_notification_delay(token, delay)

        if response["status_code"] == 200:
            await call.message.answer(text=DATA_UPDATED_SUCCESSFUL, reply_markup=kb())
        else:
            match response["data"]["error"]:
                case ErrorMessage.TOKEN_IS_EXPIRED:
                    await call.message.answer(text=SOMETHING_WITH_MY_MEMORY, reply_markup=ReplyKeyboardRemove())
                    await call.message.answer(text=CHOOSE_YOUR_ROLE_AGAIN, reply_markup=roles_kb())
                case _:
                    await call.message.answer(text=SOMETHING_WENT_WRONG, reply_markup=None)
    except Exception as e:
        print(e)
