from aiohttp import ClientSession

from service.service import Service


class UserService(Service):
    def __init__(self):
        super().__init__()
        self.__url = "/api/v1/auth"
        self.__headers = {
            "Content-Type": "application/json"
        }

    async def log_in(self, email, password):
        async with ClientSession() as session:
            body = {
                "email": email,
                "password": password
            }

            return await self.post(
                session=session,
                url=f"{self.__url}/login",
                headers=self.__headers,
                body=body
            )

    async def sign_up(self, email, password, full_name, telegram):
        async with ClientSession() as session:
            body = {
                "email": email,
                "password": password,
                "role": "student",
                "fullName": full_name,
                "telegram": telegram
            }

            return await self.post(
                session=session,
                url=f"{self.__url}/signup",
                headers=self.__headers,
                body=body
            )
