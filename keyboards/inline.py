from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def inline_keyboard(kb_list):
    return InlineKeyboardMarkup(
        inline_keyboard=kb_list
    )

def roles_kb():
    kb_list = [
        [InlineKeyboardButton(text="Студент 👨‍🎓", callback_data="student")],
        [InlineKeyboardButton(text="Админ 🔑", callback_data="admin")]
    ]

    return inline_keyboard(kb_list)

def auth_kb():
    kb_list = [
        [InlineKeyboardButton(text="Создать аккаунт", callback_data="signup")],
        [InlineKeyboardButton(text="Войти", callback_data="login")]
    ]

    return inline_keyboard(kb_list)

def back_kb():
    kb_list = [
        [InlineKeyboardButton(text="Назад 🔙", callback_data="back")]
    ]

    return inline_keyboard(kb_list)

def faculties_with_id_kb(faculties: dict):
    kb_list = []

    for name in faculties:
        kb_list.append(
            [InlineKeyboardButton(
                text=name,
                callback_data=str(faculties[name])
            )]
        )

    return inline_keyboard(kb_list)

def programs_with_id_kb(programs: dict):
    kb_list = []

    for name in programs:
        kb_list.append(
            [InlineKeyboardButton(
                text=name,
                callback_data=str(programs[name])
            )]
        )

    kb_list.append(
        [InlineKeyboardButton(
            text="Назад 🔙",
            callback_data="back"
        )]
    )

    return inline_keyboard(kb_list)

def programs_kb(programs: list):
    kb_list = []

    for name in programs:
        kb_list.append(
            [InlineKeyboardButton(
                text=name,
                callback_data=name
            )]
        )

    kb_list.append(
        [InlineKeyboardButton(
            text="Назад 🔙",
            callback_data="back"
        )]
    )

    return inline_keyboard(kb_list)

def all_groups_kb(groups: dict):
    kb_list = []

    for short_name in groups:
        kb_list.append(
            [InlineKeyboardButton(
                text=short_name,
                callback_data=str(groups[short_name])
            )]
        )

    kb_list.append(
        [InlineKeyboardButton(
            text="Назад 🔙",
            callback_data="back"
        )]
    )

    return inline_keyboard(kb_list)
