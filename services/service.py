import json


class Service:
    def __init__(self):
        self.__BASE_URL = "http://localhost:8080"

    async def get(self, session, url, headers):
        async with session.get(self.__BASE_URL + url, headers=headers) as response:
            status_code = response.status
            response_data = await response.json()
            return {"status_code": status_code, "data": response_data}

    async def post(self, session, url, headers, body = None):
        if body is None:
            async with session.post(self.__BASE_URL + url, headers=headers) as response:
                status_code = response.status
                response_data = await response.json()
                return {"status_code": status_code, "data": response_data}

        async with session.post(self.__BASE_URL + url, data=json.dumps(body), headers=headers) as response:
            status_code = response.status
            response_data = await response.json()
            return {"status_code": status_code, "data": response_data}

    async def patch(self, session, url, headers, body):
        async with session.patch(self.__BASE_URL + url, data=json.dumps(body), headers=headers) as response:
            status_code = response.status
            response_data = await response.json()
            return {"status_code": status_code, "data": response_data}
