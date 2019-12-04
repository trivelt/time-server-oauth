import requests_async


class TimeServerProxy:
    TIME_SERVER_URL = "http://127.0.0.1:9002"

    @staticmethod
    async def get_time(endpoint, token):
        url = f"{TimeServerProxy.TIME_SERVER_URL}/{endpoint}"
        response = await requests_async.get(url, headers={"Authorization": f"Bearer {token}"})
        return response.json()
