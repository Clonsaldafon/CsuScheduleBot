from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from consts.kb import ButtonText


def admin_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.CREATE_GROUP))
    builder.add(KeyboardButton(text=ButtonText.EDIT_SCHEDULE))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def choose_faculty_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.CHOOSE_FACULTY))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def no_joined_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.NOTIFICATIONS))
    builder.add(KeyboardButton(text=ButtonText.GROUPS))
    return builder.adjust(2).as_markup(resize_keyboard=True, one_time_keyboard=True)

def joined_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.NOTIFICATIONS))
    builder.add(KeyboardButton(text=ButtonText.MY_GROUP))
    builder.add(KeyboardButton(text=ButtonText.SCHEDULE))
    builder.add(KeyboardButton(text=ButtonText.ANOTHER_GROUP_SCHEDULE))
    return builder.adjust(2, 2, 1).as_markup(resize_keyboard=True, one_time_keyboard=True)
