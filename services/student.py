from aiohttp import ClientSession

from services.service import Service


class StudentService(Service):
    def __init__(self):
        super().__init__()
        self.__url = "/api/v1/users"

    async def update_full_name(self, token, full_name):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            body = {
                "full_name": full_name
            }

            return await self.patch(
                session=session,
                url=f"{self.__url}/settings",
                headers=headers,
                body=body
            )

    async def update_notifications_enabled(self, token, enabled):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            body = {
                "notifications_enabled": enabled
            }

            return await self.patch(
                session=session,
                url=f"{self.__url}/settings",
                headers=headers,
                body=body
            )

    async def update_notification_delay(self, token, delay):
        async with ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            body = {
                "notification_delay": delay
            }

            return await self.patch(
                session=session,
                url=f"{self.__url}/settings",
                headers=headers,
                body=body
            )
