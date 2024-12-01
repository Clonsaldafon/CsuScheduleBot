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
