from aiogram.fsm.state import StatesGroup, State


class AdminSignUp(StatesGroup):
    email = State()
    password = State()


class AdminLogIn(StatesGroup):
    email = State()
    password = State()