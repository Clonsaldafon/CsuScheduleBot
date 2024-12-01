from aiogram.fsm.state import StatesGroup, State


class Group(StatesGroup):
    faculty = State()
    program = State()
    group_id = State()
    my_group_id = State()