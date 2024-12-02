from aiogram.fsm.state import StatesGroup, State


class StudentSignUp(StatesGroup):
    fullname = State()

class StudentLogIn(StatesGroup):
    fullname = State()

class StudentEditProfile(StatesGroup):
    fullname = State()
    notifications_enabled = State()
    notification_delay = State()