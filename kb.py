from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup


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

    for group in groups:
        kb_list.append(
            [InlineKeyboardButton(
                text=f"{group["short_name"]}",
                callback_data=f"{group["group_id"]}"
            )]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=kb_list
    )