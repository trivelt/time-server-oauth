from aiohttp import web
import requests_async
import asyncio
from datetime import datetime
from time import time


class AuthServiceApplication(web.Application):
    VALIDATE_TOKEN_URL = "http://127.0.0.1:9001/validate_token"

    def __init__(self):
        web.Application.__init__(self)
        self.configure_routes()

    def configure_routes(self):
        self.router.add_route('GET', '/current_time', self.current_time)
        self.router.add_route('GET', '/epoch_time', self.epoch_time)

    async def current_time(self, request):
        verified = await self.verify_token(request)
        if not verified:
            return web.json_response({"error": "Token authorization failed"}, status=401)
        return self.prepare_response(str(datetime.now()))

    async def epoch_time(self, request):
        await self.verify_token(request)
        verified = await self.verify_token(request)
        if not verified:
            return web.json_response({"error": "Token authorization failed"}, status=401)
        return self.prepare_response(int(time()))

    async def verify_token(self, request):
        authorization_header = request.headers.get('Authorization', None)
        if not authorization_header or "Bearer" not in authorization_header:
            return False

        token = authorization_header[len("Bearer "):]
        response = await requests_async.get(AuthServiceApplication.VALIDATE_TOKEN_URL, params={
            "access_token": token,
            "audience": "TimeServer"
        })
        data = response.json()
        if 'valid' in data and data['valid'] == True:
            return self.verify_scope(request, data)
        return False

    def verify_scope(self, request, data):
        print("PATH: " + str(request.path))
        return 'scope' in data and data['scope'] == request.path[1:]

    def prepare_response(self, value):
        return web.json_response({"time": value}, status=200)


if __name__ == '__main__':
    port = 9002
    app = AuthServiceApplication()
    web.run_app(app, port=port)
