from aiohttp import ClientSession

from services.service import Service

class UserService(Service):
    def __init__(self):
        super().__init__()
        self.__url = "/api/v1/auth"
        self.__headers = {
            "Content-Type": "application/json"
        }

    async def sign_up_student(self, fullname, telegram, username):
        async with ClientSession() as session:
            body = {
                "full_name": fullname,
                "telegram_chat_id": telegram,
                "telegram_username": username
            }

            return await self.post(
                session=session,
                url=f"{self.__url}/telegram/signup",
                headers=self.__headers,
                body=body
            )

    async def log_in_student(self, telegram):
        async with ClientSession() as session:
            body = {
                "telegram_chat_id": telegram
            }

            return await self.post(
                session=session,
                url=f"{self.__url}/telegram/login",
                headers=self.__headers,
                body=body
            )

    async def sign_up_admin(self, email, password):
        async with ClientSession() as session:
            body = {
                "email": email,
                "password": password
            }

            return await self.post(
                session=session,
                url=f"{self.__url}/signup",
                headers=self.__headers,
                body=body
            )

    async def log_in_admin(self, email, password):
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

    async def who(self, token):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            return await self.get(
                session=session,
                url=f"{self.__url}/who",
                headers=headers
            )
