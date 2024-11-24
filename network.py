import json


BASE_URL = "http://localhost:8080"


async def get(session, url, headers):
    async with session.get(BASE_URL + url, headers=headers) as response:
        return await response.json()


async def post(session, url, headers, data = None):
    if data is None:
        async with session.post(BASE_URL + url, headers=headers) as response:
            return await response.json()

    async with session.post(BASE_URL + url, data=json.dumps(data), headers=headers) as response:
        return await response.json()

