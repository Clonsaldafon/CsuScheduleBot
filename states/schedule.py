from aiogram.fsm.state import StatesGroup, State


class Schedule(StatesGroup):
    faculty = State()
    program = State()
    group_id = State()
    schedule_type = State()
    schedule_type_selected = State()