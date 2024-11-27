from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db import redis_client
from keyboards.reply import schedule_kb, groups_kb
from service.group import GroupService
from states.group import Group
from keyboards.inline import auth_kb, all_groups_kb


group_router = Router()
group_service = GroupService()
all_groups = dict()

@group_router.message(F.text == "Группы")
async def all_groups_handler(msg: Message, state: FSMContext):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        response = await group_service.get_all_groups(token)

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
                    await state.clear()
        else:
            global all_groups
            groups = dict()
            group_ids = []

            for group in response:
                groups[group["short_name"]] = group["group_id"]
                group_ids.append(str(group["group_id"]))
            all_groups = groups

            await state.set_state(Group.id)
            await msg.answer(
                text="Выбери свою группу, чтобы присоединиться ⤵",
                reply_markup=all_groups_kb(groups)
            )
    except Exception as e:
        print(e)

@group_router.callback_query(F.data, Group.id)
async def group_handler(call: CallbackQuery, state: FSMContext):
    group_id = call.data

    await state.update_data(id=group_id)
    await state.set_state(Group.code)

    await call.message.answer(
        text="Упс, доступ запрещен 🫣\n"
             "Нужно ввести код. Я уверен, твой староста тебе поможет 😉"
    )

@group_router.message(F.text, Group.code)
async def group_join_handler(msg: Message, state: FSMContext):
    code = msg.text

    await state.update_data(code=code)
    await msg.delete()

    try:
        data = await state.get_data()
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")

        response = await group_service.join(
            token=token,
            group_id=data.get("id"),
            code=code
        )

        if "error" in response:
            match response["error"]:
                case "wrong group code" | "access denied":
                    await msg.answer(
                        text="Интересно, кто из вас ошибся? 🤔\n" +
                             "Попробуй ввести код еще раз",
                        reply_markup=all_groups_kb(all_groups)
                    )
                    await state.set_state(Group.code)
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
                        reply_markup=all_groups_kb(all_groups)
                    )
                    await state.set_state(Group.code)
        else:
            await redis_client.set(name=f"group_id:{msg.from_user.id}", value=f"{data.get("id")}")
            await msg.answer(text=f"Welcome! 🥳", reply_markup=schedule_kb())
            await state.clear()
    except Exception as e:
        print(e)

@group_router.message(F.text == "Моя группа 🫂")
async def my_group_handler(msg: Message):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        response = await group_service.get_my(token)

        if "error" in response:
            match response["error"]:
                case "token is expired":
                    await msg.answer(
                        text="Ой, что-то случилось с моей памятью 😵‍💫\n"
                             "Давай начнем сначала ⤵",
                        reply_markup=auth_kb()
                    )
        elif "group_id" in response:
            answer = group_service.get_info(response)

            await msg.answer(
                text=answer,
                reply_markup=schedule_kb()
            )
        else:
            answer = "Вот группы, в которых ты состоишь:\n\n"
            for group in response:
                answer += group_service.get_info(group)

            await msg.answer(
                text=answer,
                reply_markup=schedule_kb()
            )
    except Exception as e:
        print(e)

@group_router.message(F.text == "Покинуть группу ❌")
async def leave_group_handler(msg: Message):
    try:
        token = await redis_client.get(f"tg_id:{msg.from_user.id}")
        response = await group_service.leave(token)

        await msg.answer(
            text="Надеюсь, ты не забыл попрощаться с одногруппниками? 🫠",
            reply_markup=groups_kb()
        )
    except Exception as e:
        print(e)
