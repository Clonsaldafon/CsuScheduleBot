from aiohttp import ClientSession

from services.service import Service


class UniversityStructureService(Service):
    def __init__(self):
        super().__init__()
        self.__url = "/api/v1/edu"

    async def get_faculties(self, token):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.get(
                session=session,
                url=f"{self.__url}/faculties",
                headers=headers
            )

    async def get_programs(self, token, faculty_id):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.get(
                session=session,
                url=f"{self.__url}/faculties/{faculty_id}/programs",
                headers=headers
            )
