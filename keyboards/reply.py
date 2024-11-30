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

def admin_kb():
    kb_list = [
        [KeyboardButton(text="Создать группу 👥")],
        [KeyboardButton(text="Редактировать расписание 🗓️")]
    ]

    return reply_keyboard(kb_list)

def choose_faculty_kb():
    kb_list = [
        [KeyboardButton(text="Выбрать факультет")]
    ]

    return reply_keyboard(kb_list)

def no_subscribed_kb():
    kb_list = [
        [KeyboardButton(text="Расписание на сегодня 🗓")],
        [KeyboardButton(text="Расписание на неделю 🗓")],
        [KeyboardButton(text="Подписаться на группу 🔔")],
        [KeyboardButton(text="Вернуться к выбору группы 🔙")]
    ]

    return reply_keyboard(kb_list)

def subscribed_kb():
    kb_list = [
        [KeyboardButton(text="Расписание на сегодня 🗓")],
        [KeyboardButton(text="Расписание на неделю 🗓")],
        [KeyboardButton(text="Моя группа 🫂")],
        [KeyboardButton(text="Отписаться 🔕")]
    ]

    return reply_keyboard(kb_list)