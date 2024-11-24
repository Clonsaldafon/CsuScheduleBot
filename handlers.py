import emoji

from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiohttp import ClientSession

from kb import groups_kb, all_groups_kb, schedule_kb, auth_kb, to_start_kb
from db import redis_client
from network import post, get

router = Router()

groups = dict()
group_ids = []

my_groups = dict()
my_group_ids = []

class RegistrationStates(StatesGroup):
    email = State()
    password = State()
    fullName = State()


class AuthorizationStates(StatesGroup):
    email = State()
    password = State()


class GroupStates(StatesGroup):
    id = State()
    code = State()
    my_group_id = State()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(
        text="Привет 👋\n" +
             "Давай знакомиться, для этого создай новый аккаунт либо войди в существующий ⤵",
        reply_markup=auth_kb()
    )


@router.callback_query(F.data.in_({"login", "signup"}))
async def auth_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    data = call.data

    match data:
        case "login":
            await call.message.answer(
                text="Хм... Я тебя не помню 🤔\n" +
                     "Напиши свой email 📧",
                reply_markup=to_start_kb()
            )

            await state.set_state(AuthorizationStates.email)
        case "signup":
            await call.message.answer(
                text="Я рад, что смог заинтересовать тебя 🤗\n" +
                     "Заполнишь небольшую анкету? Это займет немного времени ⏰\n" +
                     "Но зато я тебя запомню, для начала напиши свой email 📧",
                reply_markup=to_start_kb()
            )

            await state.set_state(RegistrationStates.email)


@router.message(F.text == "В начало 🔙")
async def to_start_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        text="Создай новый аккаунт либо войди в существующий ⤵",
        reply_markup=auth_kb()
    )


@router.message(F.text, AuthorizationStates.email)
async def capture_email_auth(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(
        text="Как-будто что-то знакомое... 🤔\n" +
             "А какой пароль? 🔒",
        reply_markup=to_start_kb()
    )
    await state.set_state(AuthorizationStates.password)


@router.message(F.text, AuthorizationStates.password)
async def capture_password_auth(msg: Message, state: FSMContext):
    await state.update_data(password=msg.text)
    await msg.delete()
    data = await state.get_data()

    try:
        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "email": data.get("email"),
            "password": data.get("password")
        }

        async with ClientSession() as session:
            response = await post(
                session=session,
                url="/api/v1/auth/login",
                headers=headers,
                data=body
            )
            print(response)

            if "access_token" in response:
                await redis_client.set(
                    name=f"tg_id:{msg.from_user.id}",
                    value=str(response["access_token"])
                )
                await state.clear()

                is_group_id_exists = await redis_client.exists(f"group_id:{msg.from_user.id}")
                if is_group_id_exists:
                    await msg.answer(
                        text="Теперь вспомнил 🤪\n" +
                             "Как же я мог тебя забыть 🤦‍♂️",
                        reply_markup=schedule_kb()
                    )
                else:
                    await msg.answer(
                        text="Теперь вспомнил 🤪\n" +
                             "Как же я мог тебя забыть 🤦‍♂️",
                        reply_markup=groups_kb()
                    )
            else:
                match response["error"]:
                    case "user not found":
                        await msg.answer(
                            text="Никак не могу вспомнить человека с таким email 😔\n" +
                                 "Попробуй использовать другой адрес",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(AuthorizationStates.email)
                    case "Key: 'LogInRequest.Email' Error:Field validation for 'Email' failed on the 'email' tag":
                        await msg.answer(
                            text="Неверный формат email 🧐\n" +
                                 "Попробуй еще раз",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(AuthorizationStates.email)
                    case "wrong password":
                        await msg.answer(
                            text="Неверный пароль 🔒\n" +
                                 "Попробуй ввести его еще раз",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(AuthorizationStates.password)
                    case _:
                        await msg.answer(
                            text="Похоже, что-то пошло не по плану... 🫣\n" +
                                 "Попробуй ввести email еще раз ✍",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(AuthorizationStates.email)

    except Exception as e:
        print(e)


@router.message(F.text, RegistrationStates.email)
async def capture_email(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await msg.answer(
        text="Придумай сложный пароль (не менее 8 символов) 🔒",
        reply_markup=to_start_kb()
    )
    await state.set_state(RegistrationStates.password)


@router.message(F.text, RegistrationStates.password)
async def capture_password(msg: Message, state: FSMContext):
    if 8 <= len(msg.text) <= 40:
        await state.update_data(password=msg.text)
        await msg.delete()
        await msg.answer(
            text="Я уверен, что у того, кто захочет взломать твой аккаунт, не будет столько свободного времени 🤓\n"
                 "И наконец, финальный вопрос: как тебя зовут? Напиши ФИО ✍",
            reply_markup=to_start_kb()
        )
        await state.set_state(RegistrationStates.fullName)
    else:
        await msg.delete()
        await msg.answer(
            text="Этот пароль легко взломает даже пятиклассник 🤪\n" +
                 "Придумай что-то посложнее",
            reply_markup=to_start_kb()
        )
        await state.set_state(RegistrationStates.password)


@router.message(F.text, RegistrationStates.fullName)
async def capture_fullname(msg: Message, state: FSMContext):
    await state.update_data(fullName=msg.text)
    data = await state.get_data()

    try:
        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "email": data.get("email"),
            "password": data.get("password"),
            "role": "student",
            "fullName": data.get("fullName"),
            "telegram": str(msg.from_user.id)
        }

        async with ClientSession() as session:
            response = await post(
                session=session,
                url="/api/v1/auth/signup",
                headers=headers,
                data=body
            )
            print(response)

            if "access_token" in response:
                await redis_client.set(
                    name=f"tg_id:{msg.from_user.id}",
                    value=str(response["access_token"])
                )
                await state.clear()
                await msg.answer(
                    text="Теперь-то будем знакомы! 😊",
                    reply_markup=groups_kb()
                )
                await state.clear()
            else:
                match response["error"]:
                    case "user already exists":
                        await msg.answer(
                            text="Я уже знаком с человеком, у которого такой же email 🤨\n" +
                                 "Попробуй использовать другой адрес",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(RegistrationStates.email)
                    case "Key: 'SignUpRequest.Email' Error:Field validation for 'Email' failed on the 'email' tag":
                        await msg.answer(
                            text="Неверный формат email 🧐\n" +
                                 "Попробуй еще раз",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(RegistrationStates.email)
                    case "Key: 'SignUpRequest.Password' Error:Field validation for 'Password' failed on the 'min' tag":
                        await msg.answer(
                            text="Пароль слишком простой 🙃\n" +
                                 "Придумай другой",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(RegistrationStates.password)
                    case _:
                        await msg.answer(
                            text="Похоже, что-то пошло не по плану... 🫣\n" +
                                 "Попробуй ввести email еще раз ✍",
                            reply_markup=to_start_kb()
                        )
                        await state.set_state(RegistrationStates.email)

    except Exception as e:
        print(e)


@router.message(F.text == "Группы")
async def all_groups_handler(msg: Message, state: FSMContext):
    try:
        access_token = await redis_client.get(f"tg_id:{msg.from_user.id}")

        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            response = await get(
                session=session,
                url="/api/v1/groups",
                headers=headers
            )
            print(response)

            if "error" in response:
                match response["error"]:
                    case "token is expired":
                        await msg.delete_reply_markup()
                        await msg.answer(
                            text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                                 "Давай начнем сначала ⤵",
                            reply_markup=auth_kb()
                        )
                        await state.clear()
            else:
                groups = dict()
                group_ids = []

                for group in response:
                    groups[group["short_name"]] = group["group_id"]
                    group_ids.append(str(group["group_id"]))

                await state.set_state(GroupStates.id)
                await msg.answer(
                    text="Выбери свою группу, чтобы присоединиться ⤵",
                    reply_markup=all_groups_kb(groups)
                )

    except Exception as e:
        print(e)


@router.callback_query(F.data, GroupStates.id)
async def group_handler(call: CallbackQuery, state: FSMContext):
    group_id = call.data

    await state.update_data(id=group_id)
    await state.set_state(GroupStates.code)

    await call.message.answer(
        text="Упс, доступ запрещен 🫣\n"
             "Нужно ввести код. Я уверен, твой староста тебе поможет 😉"
    )


@router.message(F.text, GroupStates.code)
async def group_join_handler(msg: Message, state: FSMContext):
    code = msg.text
    await state.update_data(code=code)
    await msg.delete()
    
    try:
        data = await state.get_data()
        access_token = await redis_client.get(f"tg_id:{msg.from_user.id}")

        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            body = {
                "code": code
            }

            response = await post(
                session=session,
                url=f"/api/v1/groups/{data.get("id")}/join",
                headers=headers,
                data=body
            )
            print(response)

            if "error" in response:
                match response["error"]:
                    case "wrong group code" | "access denied":
                        await msg.answer(
                            text="Интересно, кто из вас ошибся? 🤔\n" +
                                 "Попробуй ввести код еще раз",
                            reply_markup=all_groups_kb(groups)
                        )
                        await state.set_state(GroupStates.code)
                    case "token is expired":
                        await msg.delete_reply_markup()
                        await msg.answer(
                            text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                                 "Давай начнем сначала ⤵",
                            reply_markup=auth_kb()
                        )
                        await state.clear()
                    case _:
                        await msg.answer(
                            text="Похоже, что-то пошло не по плану... 🫣\n" +
                                 "Попробуй ввести код еще раз ✍",
                            reply_markup=all_groups_kb(groups)
                        )
                        await state.set_state(GroupStates.code)
            else:
                await redis_client.set(
                    name=f"group_id:{msg.from_user.id}",
                    value=f"{data.get("id")}"
                )
                await msg.answer(
                    text=f"Welcome! 🥳",
                    reply_markup=schedule_kb()
                )
                await state.clear()

    except Exception as e:
        print(e)


@router.message(F.text == "Расписание на сегодня 🗓")
async def today_schedule_handler(msg: Message, state: FSMContext):
    try:
        access_token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        group_id = await redis_client.get(f"group_id:{msg.from_user.id}")

        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            response = await get(
                session=session,
                url=f"/api/v1/groups/my",
                headers=headers
            )
            print(response)

            if "error" in response:
                match response["error"]:
                    case "token is expired":
                        await msg.delete_reply_markup()
                        await msg.answer(
                            text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                                 "Давай начнем сначала ⤵",
                            reply_markup=auth_kb()
                        )
            elif "group_id" in response:
                response = await get(
                    session=session,
                    url=f"/api/v1/groups/{group_id}/schedule",
                    headers=headers
                )
                print(response)

                if response is None:
                    await msg.answer(
                        text="Староста еще не загрузил расписание 😪\n" +
                             "Попробуй поторопить его",
                        reply_markup=schedule_kb()
                    )
                elif "error" in response:
                    match response["error"]:
                        case "token is expired":
                            await msg.delete_reply_markup()
                            await msg.answer(
                                text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                                     "Давай начнем сначала ⤵",
                                reply_markup=auth_kb()
                            )
                else:
                    is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
                    day_of_week = datetime.today().weekday() + 1
                    answer = ""

                    for subject in response:
                        if subject["is_even"] == is_even:
                            if subject["day_of_week"] == day_of_week:
                                start_time = ":".join(str(subject["start_time"]).split(":")[:-1])
                                end_time = ":".join(str(subject["end_time"]).split(":")[:-1])
                                room = f"ауд. {subject["room"]}"

                                answer += f"💥 {subject["subject_name"]}\n"
                                answer += f"📖 {subject["type"]}\n"
                                answer += f"👨‍🏫 {subject["teacher"]}\n"
                                answer += f"🔢 {room}, {subject["building"]["name"]} ({subject["building"]["address"]})\n"
                                answer += f"⏰ {start_time} - {end_time}\n"
                                answer += "\n"

                    await msg.answer(
                        text=answer,
                        reply_markup=schedule_kb()
                    )
            else:
                my_groups = dict()
                my_group_ids = []
                for group in response:
                    my_groups[group["short_name"]] = group["group_id"]
                    my_group_ids.append(str(group["group_id"]))

                await state.set_state(GroupStates.my_group_id)
                await msg.answer(
                    text="Я вижу, что ты состоишь в нескольких группах 🧐\n"
                         "Какое именно расписание ты хочешь посмотреть?",
                    reply_markup=all_groups_kb(my_groups)
                )

    except Exception as e:
        print(e)


@router.callback_query(F.data, GroupStates.my_group_id)
async def group_schedule_handler(call: CallbackQuery, state: FSMContext):
    group_id = call.data

    try:
        access_token = await redis_client.get(f"tg_id:{call.from_user.id}")

        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            response = await get(
                session=session,
                url=f"/api/v1/groups/{group_id}/schedule",
                headers=headers
            )
            print(response)

            if response == "None":
                await call.message.answer(
                    text="Староста еще не загрузил расписание 😪\n" +
                         "Попробуй поторопить его",
                    reply_markup=schedule_kb()
                )
            elif "error" in response:
                match response["error"]:
                    case "token is expired":
                        await call.message.delete_reply_markup()
                        await call.message.answer(
                            text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                                 "Давай начнем сначала ⤵",
                            reply_markup=auth_kb()
                        )
            else:
                is_even = (datetime.today().isocalendar().week + 1) % 2 == 0
                day_of_week = datetime.today().weekday() + 1
                answer = ""

                for subject in response:
                    if subject["is_even"] == is_even:
                        if subject["day_of_week"] == day_of_week:
                            start_time = ":".join(str(subject["start_time"]).split(":")[:-1])
                            end_time = ":".join(str(subject["end_time"]).split(":")[:-1])
                            room = f"ауд. {subject["room"]}"

                            answer += f"💥 {subject["subject_name"]}\n"
                            answer += f"📖 {subject["type"]}\n"
                            answer += f"👨‍🏫 {subject["teacher"]}\n"
                            answer += f"🔢 {room}, {subject["building"]["name"]} ({subject["building"]["address"]})\n"
                            answer += f"⏰{start_time} - {end_time}\n"
                            answer += "\n"

                await call.message.answer(
                    text=answer,
                    reply_markup=schedule_kb()
                )
            await state.clear()

    except Exception as e:
        print(e)


@router.message(F.text == "Моя группа 🫂")
async def my_group_handler(msg: Message):
    try:
        access_token = await redis_client.get(f"tg_id:{msg.from_user.id}")

        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            response = await get(
                session=session,
                url=f"/api/v1/groups/my",
                headers=headers
            )
            print(response)

            if "error" in response:
                match response["error"]:
                    case "token is expired":
                        await msg.delete_reply_markup()
                        await msg.answer(
                            text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                                 "Давай начнем сначала ⤵",
                            reply_markup=auth_kb()
                        )
            elif "group_id" in response:
                is_schedule_exists = "да" if response["exists_schedule"] else "нет"

                answer = f"🏛 {response["faculty"]}\n"
                answer += f"📚 {response["program"]}\n"
                answer += f"✨ {response["short_name"]}\n"
                answer += f"🫂 Количество участников: {response["number_of_people"]}\n"
                answer += f"🗓 Расписание загружено: {is_schedule_exists}\n"

                await msg.answer(
                    text=answer,
                    reply_markup=schedule_kb()
                )
            else:
                answer = "Вот группы, в которых ты состоишь:\n\n"
                for group in response:
                    is_schedule_exists = "да" if group["exists_schedule"] else "нет"

                    answer += f"🏛 {group["faculty"]}\n"
                    answer += f"📚 {group["program"]}\n"
                    answer += f"✨ {group["short_name"]}\n"
                    answer += f"🫂 Количество участников: {group["number_of_people"]}\n"
                    answer += f"🗓 Расписание загружено: {is_schedule_exists}\n"
                    answer += "\n"

                await msg.answer(
                    text=answer,
                    reply_markup=schedule_kb()
                )

    except Exception as e:
        print(e)

@router.message(F.text == "Покинуть группу ❌")
async def leave_group_handler(msg: Message):
    try:
        access_token = await redis_client.get(f"tg_id:{msg.from_user.id}")

        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }

            response = await post(
                session=session,
                url=f"/api/v1/groups/leave",
                headers=headers
            )
            print(response)

            await msg.answer(
                text="Надеюсь, ты не забыл попрощаться с одногруппниками? 🫠",
                reply_markup=groups_kb()
            )

    except Exception as e:
        print(e)
