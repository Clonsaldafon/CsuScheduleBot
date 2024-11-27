from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def reply_keyboard(kb_list):
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def to_start_kb():
    kb_list = [
        [KeyboardButton(text="В начало 🔙")]
    ]

    return reply_keyboard(kb_list)

def choose_faculty_kb():
    kb_list = [
        [KeyboardButton(text="Выбрать факультет")]
    ]

    return reply_keyboard(kb_list)

def schedule_kb():
    kb_list = [
        [KeyboardButton(text="Расписание на сегодня 🗓")],
        [KeyboardButton(text="Расписание на неделю 🗓")],
        [KeyboardButton(text="Моя группа 🫂")],
        [KeyboardButton(text="Покинуть группу ❌")]
    ]

    return reply_keyboard(kb_list)