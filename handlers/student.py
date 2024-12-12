import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from consts.bot_answer import DATA_UPDATED_SUCCESSFUL, \
    CHOOSE_NOTIFICATION_DELAY, SOMETHING_WENT_WRONG, \
    START_ANSWER, SUPPORT_ANSWER, NOTIFICATIONS_WARNING
from consts.kb import ButtonText, CallbackData
from database.db import redis_client
from keyboards.inline import notifications_kb, notification_delay_kb
from keyboards.reply import joined_kb, no_joined_kb
from middlewares.auth import auth_middleware
from services.student import student_service
from services.auth import auth_service
from states.student import StudentProfile

student_router = Router()

student_router.message.middleware(auth_middleware)
student_router.callback_query.middleware(auth_middleware)

is_notifications_enabled = False
student_notifications_answer = ""
is_joined = ""

@student_router.message(F.text == ButtonText.NOTIFICATIONS)
async def notifications_handler(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(f"chat_id:{msg.chat.id}")
        global is_joined
        is_joined = await redis_client.get(f"joined:{msg.chat.id}")
        kb = joined_kb if (is_joined == "true") else no_joined_kb

        try:
            response = await auth_service.who(token)

            if "data" in response:
                if "error" in response["data"]:
                    await msg.answer(text=SOMETHING_WENT_WRONG, reply_markup=kb())
                else:
                    global is_notifications_enabled
                    is_notifications_enabled = response["data"]["notifications_enabled"]

                    answer = f"<b>Уведомления:</b> {"включены" if is_notifications_enabled else "отключены"}"
                    if is_notifications_enabled:
                        answer += f"\nУведомлять за <b>{response["data"]["notification_delay"]} мин.</b> до пары"
                    if is_notifications_enabled and is_joined != "true":
                        answer += f"\n\n{NOTIFICATIONS_WARNING}"

                    answer += f"\n\n{SUPPORT_ANSWER}"

                    global student_notifications_answer
                    student_notifications_answer = answer
                    await msg.answer(text=answer, reply_markup=notifications_kb(is_notifications_enabled))
                    await state.set_state(StudentProfile.notifications)
        except Exception as e:
            logging.error(msg=f"Error: {e}")
    except Exception as e:
        logging.error(msg=f"Redis error: {e}")

@student_router.callback_query(F.data == CallbackData.BACK_CALLBACK, StudentProfile.notifications)
async def back_notifications_handler(call: CallbackQuery, state: FSMContext):
    kb = joined_kb if (is_joined == "true") else no_joined_kb
    await call.message.delete()
    await call.message.answer(text=START_ANSWER, reply_markup=kb())
    await state.clear()

@student_router.callback_query(F.data == CallbackData.BACK_CALLBACK, StudentProfile.notifications_enabling)
async def back_edit_notifications_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text=student_notifications_answer,
        reply_markup=notifications_kb(is_notifications_enabled)
    )
    await state.set_state(StudentProfile.notifications)

@student_router.callback_query(F.data.in_({
    CallbackData.ENABLE_NOTIFICATIONS_CALLBACK,
    CallbackData.DISABLE_NOTIFICATIONS_CALLBACK
}), StudentProfile.notifications)
async def capture_notifications_enabling(call: CallbackQuery, state: FSMContext):
    enabled = call.data == CallbackData.ENABLE_NOTIFICATIONS_CALLBACK
    await state.update_data(notifications_enabling=enabled)
    await notifications_enabling(call, state)

async def notifications_enabling(call: CallbackQuery, state: FSMContext):
    enabled = await state.get_value("notifications_enabling")

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        global is_joined
        is_joined = await redis_client.get(f"joined:{call.message.chat.id}")
        kb = joined_kb if (is_joined == "true") else no_joined_kb

        if enabled:
            await call.message.edit_text(
                text=CHOOSE_NOTIFICATION_DELAY,
                reply_markup=notification_delay_kb()
            )
            await state.set_state(StudentProfile.notification_delay)
        else:
            try:
                response = await student_service.update_notifications(token, enabled)

                if "data" in response:
                    if "error" not in response["data"]:
                        await call.message.delete()
                        await call.message.answer(text=DATA_UPDATED_SUCCESSFUL, reply_markup=kb())
                        await state.clear()
            except Exception as e:
                logging.error(msg=f"Error: {e}")
    except Exception as e:
        logging.error(msg=f"Redis error: {e}")

@student_router.callback_query(F.data == CallbackData.NOTIFICATIONS_DELAY_CALLBACK)
async def edit_notification_delay_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text=CHOOSE_NOTIFICATION_DELAY, reply_markup=notification_delay_kb())
    await state.set_state(StudentProfile.notification_delay)

@student_router.callback_query(F.data == CallbackData.BACK_CALLBACK, StudentProfile.notification_delay)
async def back_edit_notifications_delay_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text=student_notifications_answer,
        reply_markup=notifications_kb(is_notifications_enabled)
    )
    await state.set_state(StudentProfile.notifications)

@student_router.callback_query(F.data.in_({
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_5",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_10",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_20",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_30",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_45",
    f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_60"
}), StudentProfile.notification_delay)
async def capture_edit_notification_delay(call: CallbackQuery, state: FSMContext):
    delay = int(call.data.split("_")[-1])

    try:
        token = await redis_client.get(f"chat_id:{call.message.chat.id}")
        global is_joined
        is_joined = await redis_client.get(f"joined:{call.message.chat.id}")
        kb = joined_kb if (is_joined == "true") else no_joined_kb

        enabled = await state.get_value("notifications_enabling")

        try:
            response = await student_service.update_notifications(token, enabled, delay)

            if "data" in response:
                if "error" not in response["data"]:
                    await call.message.delete()
                    await call.message.answer(text=DATA_UPDATED_SUCCESSFUL, reply_markup=kb())
                    await state.clear()
        except Exception as e:
            logging.error(msg=f"Error: {e}")
    except Exception as e:
        logging.error(msg=f"Redis error: {e}")
