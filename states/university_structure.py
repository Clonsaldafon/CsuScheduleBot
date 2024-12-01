from aiogram.fsm.state import StatesGroup, State


class UniversityStructure(StatesGroup):
    faculty_id = State()
    program_id = State()
    short_name = State()