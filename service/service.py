import json


class Service:
    def __init__(self):
        self.__BASE_URL = "http://localhost:8080"

    async def get(self, session, url, headers):
        async with session.get(self.__BASE_URL + url, headers=headers) as response:
            return await response.json()

    async def post(self, session, url, headers, body = None):
        if body is None:
            async with session.post(self.__BASE_URL + url, headers=headers) as response:
                return await response.json()

        async with session.post(self.__BASE_URL + url, data=json.dumps(body), headers=headers) as response:
            return await response.json()
