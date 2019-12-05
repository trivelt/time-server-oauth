import requests_async


class TimeServerProxy:
    TIME_SERVER_URL = "https://127.0.0.1:9002"

    @staticmethod
    async def get_time(endpoint, token):
        try:
            url = f"{TimeServerProxy.TIME_SERVER_URL}/{endpoint}"
            response = await requests_async.get(url, headers={"Authorization": f"Bearer {token}"}, verify=False)
        except requests_async.exceptions.ConnectionError as e:
            print("Error: cannot connect to the time server" + str(e))
            return 500, {"error": str(e)}
        return 200, response.json()
