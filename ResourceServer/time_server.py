from aiohttp import web
import requests_async
import asyncio
from datetime import datetime
from time import time


class AuthServiceApplication(web.Application):
    def __init__(self):
        web.Application.__init__(self)
        self.configure_routes()

    def configure_routes(self):
        self.router.add_route('GET', '/current_time', self.current_time)
        self.router.add_route('GET', '/epoch_time', self.epoch_time)

    async def current_time(self, request):
        # try:
        await self.verify_token(request)
        return self.prepare_response(str(datetime.now()))
        # except Exception as e:
        #     print(e)
        #     return web.json_response({"error": "Invalid token"}, status=400)

    async def epoch_time(self, request):
        await self.verify_token(request)
        return self.prepare_response(int(time()))

    async def verify_token(self, request):
        data = request.headers
        token = data['Authorization']
        print("Verifying token " + str(token))

    def prepare_response(self, value):
        return web.json_response({"time": value}, status=200)

if __name__ == '__main__':
    port = 9002
    app = AuthServiceApplication()
    web.run_app(app, port=port)
