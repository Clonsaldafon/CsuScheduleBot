from aiogram.fsm.state import StatesGroup, State


class SignUp(StatesGroup):
    email = State()
    password = State()
    fullName = State()


class LogIn(StatesGroup):
    email = State()
    password = State()