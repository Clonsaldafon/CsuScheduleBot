from datetime import datetime

from aiohttp import ClientSession

from services.service import Service


class ScheduleService(Service):
    def __init__(self):
        super().__init__()
        self.__url = "/api/v1/groups"

    def get_info(self, subject):
        start_time = ":".join(str(subject["start_time"]).split(":")[:-1])
        end_time = ":".join(str(subject["end_time"]).split(":")[:-1])
        room = f"ауд. {subject["room"]}"

        return (f"💥 {subject["subject_name"]}\n"
                f"📖 {subject["type"]}\n"
                f"👨‍🏫 {subject["teacher"]}\n"
                f"🔢 {room}, {subject["building"]["name"]} ({subject["building"]["address"]})\n"
                f"⏰ {start_time} - {end_time}\n\n")

    async def get_schedule(self, token, group_id, is_even):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.get(
                session=session,
                url=f"{self.__url}/{group_id}/schedule?week_even={str(is_even).lower()}",
                headers=headers
            )
