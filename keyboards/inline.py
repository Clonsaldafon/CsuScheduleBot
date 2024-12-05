from cgitb import reset

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from consts.kb import ButtonText, CallbackData


def roles_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=ButtonText.STUDENT, callback_data=CallbackData.STUDENT_CALLBACK))
    builder.add(InlineKeyboardButton(text=ButtonText.ADMIN, callback_data=CallbackData.ADMIN_CALLBACK))
    return builder.adjust(2).as_markup(resize_keyboard=True)

def auth_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=ButtonText.SIGN_UP, callback_data=CallbackData.SIGN_UP_CALLBACK))
    builder.add(InlineKeyboardButton(text=ButtonText.LOG_IN, callback_data=CallbackData.LOG_IN_CALLBACK))
    return builder.adjust(2).as_markup(resize_keyboard=True)

def back_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=ButtonText.BACK, callback_data=CallbackData.BACK_CALLBACK))
    return builder.as_markup(resize_keyboard=True)

def faculties_with_id_kb(faculties: dict):
    builder = InlineKeyboardBuilder()
    for name in faculties:
        builder.add(InlineKeyboardButton(text=name, callback_data=str(faculties[name])))
    return builder.adjust(1).as_markup(resize_keyboard=True)

def programs_with_id_kb(programs: dict):
    builder = InlineKeyboardBuilder()
    for name in programs:
        builder.add(InlineKeyboardButton(text=name, callback_data=str(programs[name])))
    builder.add(InlineKeyboardButton(text=ButtonText.BACK, callback_data=CallbackData.BACK_CALLBACK))
    return builder.adjust(1).as_markup(resize_keyboard=True)

def programs_kb(programs: list):
    builder = InlineKeyboardBuilder()
    for name in programs:
        builder.add(InlineKeyboardButton(text=name, callback_data=name))
    builder.add(InlineKeyboardButton(text=ButtonText.BACK, callback_data=CallbackData.BACK_CALLBACK))
    return builder.adjust(1).as_markup(resize_keyboard=True)

def all_groups_kb(groups: dict):
    builder = InlineKeyboardBuilder()
    for short_name in groups:
        builder.add(InlineKeyboardButton(text=short_name, callback_data=str(groups[short_name])))
    builder.add(InlineKeyboardButton(text=ButtonText.BACK, callback_data=CallbackData.BACK_CALLBACK))
    return builder.adjust(1).as_markup(resize_keyboard=True)

def schedule_types_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=ButtonText.TODAY_SCHEDULE, callback_data=CallbackData.TODAY_CALLBACK))
    builder.add(InlineKeyboardButton(text=ButtonText.WEEK_SCHEDULE, callback_data=CallbackData.WEEK_CALLBACK))
    builder.add(InlineKeyboardButton(text=ButtonText.NEXT_WEEK_SCHEDULE, callback_data=CallbackData.NEXT_WEEK_CALLBACK))
    return builder.adjust(2, 1).as_markup(resize_keyboard=True)

def profile_kb(is_joined: str):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=ButtonText.EDIT_FULL_NAME,
        callback_data=CallbackData.EDIT_FULL_NAME_CALLBACK)
    )
    if is_joined == "true":
        builder.add(InlineKeyboardButton(
            text=ButtonText.EDIT_NOTIFICATIONS,
            callback_data=CallbackData.EDIT_NOTIFICATIONS_CALLBACK)
        )
    return builder.adjust(1).as_markup(resize_keyboard=True)

def notifications_kb(enabled: bool):
    builder = InlineKeyboardBuilder()

    if enabled:
        builder.add(InlineKeyboardButton(
            text=ButtonText.DISABLE_NOTIFICATIONS,
            callback_data=CallbackData.DISABLE_NOTIFICATIONS_CALLBACK)
        )
        builder.add(InlineKeyboardButton(
            text=ButtonText.NOTIFICATIONS_DELAY,
            callback_data=CallbackData.NOTIFICATIONS_DELAY_CALLBACK)
        )
    else:
        builder.add(InlineKeyboardButton(
            text=ButtonText.ENABLE_NOTIFICATIONS,
            callback_data=CallbackData.ENABLE_NOTIFICATIONS_CALLBACK)
        )

    return builder.adjust(1).as_markup(resize_keyboard=True)

def notification_delay_kb():
    builder = InlineKeyboardBuilder()
    delays = [10, 20, 30, 40, 50, 60]
    for delay in delays:
        builder.add(InlineKeyboardButton(
            text=f"{delay} мин.",
            callback_data=f"{CallbackData.NOTIFICATIONS_DELAY_CALLBACK}_{delay}")
        )
    return builder.adjust(3).as_markup(resize_keyboard=True)

def feedback_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=ButtonText.FEEDBACK,
        url="https://www.google.com/search?q=cute+cats&sca_esv=34e05643fe6f2863&udm=2&biw=1920&bih=980&sxsrf=ADLYWIL"\
            "fHgZO3wL0csV5lxD9eMzprGzPMw%3A1733426899609&ei=0_5RZ7b1JNn9wPAP-unM4AY&ved=0ahUKEwj2quG0rpGKAxXZPhAIHfo"\
            "0E2wQ4dUDCBE&uact=5&oq=cute+cats&gs_lp=EgNpbWciCWN1dGUgY2F0czIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAA"\
            "GIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgARIuQVQ4QRY4QRwAXgAkAEAmAFToAGlAaoBATK4AQPIAQD4AQGYAgK"\
            "gAljCAgoQABiABBhDGIoFwgIGEAAYBxgemAMAiAYBkgcBMqAHvQo&sclient=img")
    )
    builder.add(InlineKeyboardButton(
        text=ButtonText.FEEDBACK_LATER,
        callback_data=CallbackData.FEEDBACK_LATER_CALLBACK)
    )
    return builder.adjust(1).as_markup(resize_keyboard=True)