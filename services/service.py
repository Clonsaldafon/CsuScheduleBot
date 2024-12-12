import asyncio
import json
import logging
import os
from random import randint

from aiohttp import ClientOSError, ClientResponseError
from dotenv import load_dotenv


load_dotenv()


class Service:
    def __init__(self):
        self.__BASE_URL = os.getenv("HOST_URL")
        self.__RETRIES = 3

    async def get(self, session, url, headers):
        for attempt in range(self.__RETRIES):
            try:
                async with session.get(self.__BASE_URL + url, headers=headers) as response:
                    status_code = response.status
                    response_data = await response.json()
                    return {"status_code": status_code, "data": response_data}
            except ClientOSError as e:
                logging.warning(msg=f"Connection error: {e}. Attempt {attempt + 1} of {self.__RETRIES}")
                await asyncio.sleep(3 + randint(0, 9))
            except ClientResponseError as e:
                logging.error(msg=f"Server response error: {e.status} {e.message}")
                return {"status_code": e.status, "data": { "error": e.message }}
            except Exception as e:
                logging.error(msg=f"Unexpected error: {e}")
                return
        return "Failed after retries"

    async def post(self, session, url, headers, body = None):
        if body is None:
            for attempt in range(self.__RETRIES):
                try:
                    async with session.post(self.__BASE_URL + url, headers=headers) as response:
                        status_code = response.status
                        response_data = await response.json()
                        return {"status_code": status_code, "data": response_data}
                except ClientOSError as e:
                    logging.warning(msg=f"Connection error: {e}. Attempt {attempt + 1} of {self.__RETRIES}")
                    await asyncio.sleep(3 + randint(0, 9))
                except ClientResponseError as e:
                    logging.error(msg=f"Server response error: {e.status} {e.message}")
                    return {"status_code": e.status, "data": {"error": e.message}}
                except Exception as e:
                    logging.error(msg=f"Unexpected error: {e}")
                    return
            return "Failed after retries"

        for attempt in range(self.__RETRIES):
            try:
                async with session.post(self.__BASE_URL + url, data=json.dumps(body), headers=headers) as response:
                    status_code = response.status
                    response_data = await response.json()
                    return {"status_code": status_code, "data": response_data}
            except ClientOSError as e:
                logging.warning(msg=f"Connection error: {e}. Attempt {attempt + 1} of {self.__RETRIES}")
                await asyncio.sleep(3 + randint(0, 9))
            except ClientResponseError as e:
                logging.error(msg=f"Server response error: {e.status} {e.message}")
                return {"status_code": e.status, "data": {"error": e.message}}
            except Exception as e:
                logging.error(msg=f"Unexpected error: {e}")
                return
        return "Failed after retries"

    async def patch(self, session, url, headers, body):
        for attempt in range(self.__RETRIES):
            try:
                async with session.patch(self.__BASE_URL + url, data=json.dumps(body), headers=headers) as response:
                    status_code = response.status
                    response_data = await response.json()
                    return {"status_code": status_code, "data": response_data}
            except ClientOSError as e:
                logging.warning(msg=f"Connection error: {e}. Attempt {attempt + 1} of {self.__RETRIES}")
                await asyncio.sleep(3 + randint(0, 9))
            except ClientResponseError as e:
                logging.error(msg=f"Server response error: {e.status} {e.message}")
                return {"status_code": e.status, "data": {"error": e.message}}
            except Exception as e:
                logging.error(msg=f"Unexpected error: {e}")
                return
        return "Failed after retries"
