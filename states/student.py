from aiogram.fsm.state import StatesGroup, State


class StudentProfile(StatesGroup):
    notifications = State()
    notifications_enabling = State()
    notification_delay = State()