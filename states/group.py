from aiogram.fsm.state import StatesGroup, State


class Group(StatesGroup):
    id = State()
    code = State()
    my_group_id = State()