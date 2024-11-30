from aiohttp import ClientSession

from services.service import Service


class AdminService(Service):
    def __init__(self):
        super().__init__()
        self.__url = "/api/v1/groups"
        self.__headers = {
            "Content-Type": "application/json"
        }

    async def create_group(self, token, faculty_id, program_id, short_name):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            body = {
                "faculty_id": faculty_id,
                "program_id": program_id,
                "short_Name": short_name
            }

            return await self.post(
                session=session,
                url=self.__url,
                headers=headers,
                body=body
            )
