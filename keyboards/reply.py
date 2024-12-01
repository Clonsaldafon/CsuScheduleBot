from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from consts.kb import ButtonText


def to_start_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.TO_START))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def admin_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.CREATE_GROUP))
    builder.add(KeyboardButton(text=ButtonText.EDIT_SCHEDULE))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def choose_faculty_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.CHOOSE_FACULTY))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def no_subscribed_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.TODAY_SCHEDULE))
    builder.add(KeyboardButton(text=ButtonText.WEEK_SCHEDULE))
    builder.add(KeyboardButton(text=ButtonText.SUBSCRIBE))
    builder.add(KeyboardButton(text=ButtonText.BACK_TO_GROUP_CHOICE))
    return builder.adjust(2).as_markup(resize_keyboard=True, one_time_keyboard=True)

def subscribed_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=ButtonText.TODAY_SCHEDULE))
    builder.add(KeyboardButton(text=ButtonText.WEEK_SCHEDULE))
    builder.add(KeyboardButton(text=ButtonText.MY_GROUP))
    builder.add(KeyboardButton(text=ButtonText.UNSUBSCRIBE))
    return builder.adjust(2).as_markup(resize_keyboard=True, one_time_keyboard=True)
