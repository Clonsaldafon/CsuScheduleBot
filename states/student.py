from aiogram.fsm.state import StatesGroup, State


class StudentSignUp(StatesGroup):
    fullname = State()

class StudentLogIn(StatesGroup):
    fullname = State()