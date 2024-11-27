from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def inline_keyboard(kb_list):
    return InlineKeyboardMarkup(
        inline_keyboard=kb_list
    )


def auth_kb():
    kb_list = [
        [InlineKeyboardButton(text="Создать аккаунт", callback_data="signup")],
        [InlineKeyboardButton(text="Войти", callback_data="login")]
    ]

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

    return inline_keyboard(kb_list)