from aiohttp import web
import requests_async
import asyncio


class AuthServiceApplication(web.Application):
    def __init__(self):
        web.Application.__init__(self)
        self.configure_routes()

    def configure_routes(self):
        self.router.add_route('GET', '/authorize', self.authorize)
        self.router.add_route('GET', '/get_token', self.get_token)
        self.router.add_route('GET', '/validate_token', self.validate_token)

    async def authorize(self, request):
        callback_url = request.query['callback']
        scope = request.query['scope']
        await requests_async.get(callback_url, json={"code": "SOMECODE", "scope": scope})
        return web.json_response({}, status=200)

    async def get_token(self, request):
        return web.json_response({"token": "SOMETOKEN"}, status=200)

    async def validate_token(self, request):
        return web.json_response({}, status=200)

if __name__ == '__main__':
    port = 9001
    app = AuthServiceApplication()
    web.run_app(app, port=port)

