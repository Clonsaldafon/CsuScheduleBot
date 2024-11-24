from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup


def auth_kb():
    kb_list = [
        [InlineKeyboardButton(text="Создать аккаунт", callback_data="signup")],
        [InlineKeyboardButton(text="Войти", callback_data="login")]
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=kb_list
    )


def to_start_kb():
    kb_list = [
        [KeyboardButton(text="В начало 🔙")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def groups_kb():
    kb_list = [
        [KeyboardButton(text="Группы")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def all_groups_kb(groups: dict):
    kb_list = []

    for short_name in groups:
        kb_list.append(
            [InlineKeyboardButton(
                text=short_name,
                callback_data=str(groups[short_name])
            )]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=kb_list
    )


def schedule_kb():
    kb_list = [
        [KeyboardButton(text="Расписание на сегодня 🗓")],
        [KeyboardButton(text="Моя группа 🫂")],
        [KeyboardButton(text="Покинуть группу ❌")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True
    )
