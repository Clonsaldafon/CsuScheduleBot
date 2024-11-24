from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiohttp import ClientSession

from kb import groups_kb, all_groups_kb, schedule_kb
from db import redis_client
from network import post, get

router = Router()

groups = dict()
group_ids = []


class RegistrationStates(StatesGroup):
    email = State()
    password = State()
    fullName = State()


class GroupJoiningState(StatesGroup):
    id = State()
    code = State()


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer(text="Чтобы начать пользоваться ботом, вам нужно заполнить свои данные.\n" +
                          "Для начала введите адрес электронной почты")
    await state.set_state(RegistrationStates.email)


@router.message(F.text, RegistrationStates.email)
async def capture_email(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(text="А теперь придумайте пароль для доступа к сервису")
    await state.set_state(RegistrationStates.password)


@router.message(F.text, RegistrationStates.password)
async def capture_password(msg: Message, state: FSMContext):
    await state.update_data(password=msg.text)
    await msg.delete()
    await msg.answer(text="Введите ФИО")
    await state.set_state(RegistrationStates.fullName)


@router.message(F.text, RegistrationStates.fullName)
async def capture_fullname(msg: Message, state: FSMContext):
    await state.update_data(fullName=msg.text)

    state_data = await state.get_data()

    async with ClientSession() as session:
        data = {
            "email": state_data.get("email"),
            "password": state_data.get("password"),
            "role": "student",
            "fullName": state_data.get("fullName"),
            "telegram": str(msg.from_user.id)
        }
        headers = {
            "Content-Type": "application/json"
        }

        response_json = await post(
            session=session,
            url="/v1/api/auth/signup",
            headers=headers,
            data=data
        )
        print(response_json)

        await state.update_data(access_token=response_json["access_token"])
        await state.update_data(refresh_token=response_json["refresh_token"])
        await redis_client.set(
            name=f"tg_id:{msg.from_user.id}",
            value=str(response_json["access_token"])
        )

    await msg.answer(text="Вы успешно зарегистрировались!", reply_markup=groups_kb())
    await state.clear()


@router.message(F.text == "Группы")
async def all_groups_handler(msg: Message, state: FSMContext):
    async with ClientSession() as session:
        redis_token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {redis_token}"
        }

        response_json = await get(
            session=session,
            url="/v1/api/groups",
            headers=headers
        )
        print(response_json)

        for group in response_json:
            groups[group["short_name"]] = group["group_id"]
            group_ids.append(f"{group["group_id"]}")

        await state.set_state(GroupJoiningState.id)
        await msg.answer(text="Выберите свою группу", reply_markup=all_groups_kb(response_json))


@router.callback_query(F.data.in_(group_ids), GroupJoiningState.id)
async def group_handler(call: CallbackQuery, state: FSMContext):
    group_id = call.data

    await state.update_data(id=group_id)
    await state.set_state(GroupJoiningState.code)

    await call.message.answer(text="Введите код доступа (его можно узнать у старосты)")


@router.message(F.text, GroupJoiningState.code)
async def group_join_handler(msg: Message, state: FSMContext):
    code = msg.text

    await state.update_data(code=code)

    async with ClientSession() as session:
        state_data = await state.get_data()
        redis_token = await redis_client.get(f"tg_id:{msg.from_user.id}")

        data = {
            "code": code
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {redis_token}"
        }

        response_json = await post(
            session=session,
            url=f"/v1/api/groups/{state_data.get("id")}/join",
            headers=headers,
            data=data
        )
        print(response_json)

        await redis_client.set(
            name=f"group_id:{msg.from_user.id}",
            value=f"{state_data.get("id")}"
        )
        await msg.answer(text="Welcome!", reply_markup=schedule_kb())
        await state.clear()


@router.message(F.text == "Расписание на сегодня")
async def today_schedule_handler(msg: Message):
    async with ClientSession() as session:
        redis_token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        redis_group_id = await redis_client.get(f"group_id:{msg.from_user.id}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {redis_token}"
        }

        response_json = await get(
            session=session,
            url=f"/v1/api/groups/{redis_group_id}/schedule",
            headers=headers
        )
        print(response_json)

        is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
        day_of_week = datetime.today().weekday() + 1
        answer = ""
        for subject in response_json:
            if subject["is_even"] == is_even:
                if subject["day_of_week"] == day_of_week:
                    start_time = ":".join(str(subject["start_time"]).split(":")[:-1])
                    end_time = ":".join(str(subject["end_time"]).split(":")[:-1])

                    answer += f"{subject["subject_name"]}\n"
                    answer += f"{subject["type"]}\n"
                    answer += f"{subject["teacher"]}\n"
                    answer += f"ауд. {subject["room"]}, {subject["building"]["name"]} ({subject["building"]["address"]})\n"
                    answer += f"{start_time} - {end_time}\n"
                    answer += "\n"

        await msg.answer(text=answer)

