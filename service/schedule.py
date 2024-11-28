from datetime import datetime

from aiohttp import ClientSession

from service.service import Service


class ScheduleService(Service):
    def __init__(self):
        super().__init__()
        self.__url = "/api/v1/groups"

    def get_info(self, subject):
        start_time = ":".join(str(subject["start_time"]).split(":")[:-1])
        end_time = ":".join(str(subject["end_time"]).split(":")[:-1])
        room = f"ауд. {subject["room"]}"

        info = f"💥 {subject["subject_name"]}\n"
        info += f"📖 {subject["type"]}\n"
        info += f"👨‍🏫 {subject["teacher"]}\n"
        info += f"🔢 {room}, {subject["building"]["name"]} ({subject["building"]["address"]})\n"
        info += f"⏰ {start_time} - {end_time}\n"
        info += "\n"

        return info

    async def get_for_today(self, token, group_id):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.get(
                session=session,
                url=f"{self.__url}/{group_id}/schedule",
                headers=headers
            )

    async def get_for_week(self, token, group_id):
        async with ClientSession() as session:
            is_even = (datetime.today().isocalendar().week + 1) % 2 == 0

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.get(
                session=session,
                url=f"{self.__url}/{group_id}/schedule?week_even={is_even}",
                headers=headers
            )
