from aiohttp import ClientSession

from services.service import Service


class GroupService(Service):
    def __init__(self):
        super().__init__()
        self.__url = "/api/v1/groups"

    def get_info(self, group):
        is_schedule_exists = "да" if group["exists_schedule"] else "нет"

        return (f"🏛 {group["faculty"]}\n"
                f"📚 {group["program"]}\n"
                f"✨ {group["short_name"]}\n"
                f"🫂 Количество подписчиков: {group["number_of_people"]}\n"
                f"🗓 Расписание загружено: {is_schedule_exists}\n\n")

    async def get_groups(self, token, program):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.get(
                session=session,
                url=f"{self.__url}?program={program}",
                headers=headers
            )

    async def join(self, token, group_id):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.post(
                session=session,
                url=f"{self.__url}/{group_id}/join",
                headers=headers
            )

    async def get_my(self, token):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.get(
                session=session,
                url=f"{self.__url}/me",
                headers=headers
            )

    async def leave(self, token):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.post(
                session=session,
                url=f"{self.__url}/leave",
                headers=headers
            )
