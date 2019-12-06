import ssl
import requests_async
from aiohttp import web

from time_provider import TimeProvider


class AuthServiceApplication(web.Application):
    VALIDATE_TOKEN_URL = "https://127.0.0.1:9001/validate_token"

    def __init__(self):
        web.Application.__init__(self)
        self.configure_routes()

    def configure_routes(self):
        self.router.add_route('GET', '/current_time', self.current_time)
        self.router.add_route('GET', '/epoch_time', self.epoch_time)

    async def current_time(self, request):
        return await self.send_time_response(request, TimeProvider.current_time)

    async def epoch_time(self, request):
        return await self.send_time_response(request, TimeProvider.epoch_time)

    async def send_time_response(self, request, time_function):
        await self.verify_token(request)
        verified = await self.verify_token(request)
        if not verified:
            return web.json_response({"error": "Token authorization failed"}, status=401)
        return web.json_response({"time": time_function()}, status=200)

    async def verify_token(self, request):
        authorization_header = request.headers.get('Authorization', None)
        if not authorization_header or "Bearer" not in authorization_header:
            return False

        token = authorization_header[len("Bearer "):]
        response = await requests_async.get(AuthServiceApplication.VALIDATE_TOKEN_URL, params={
            "access_token": token,
            "audience": "TimeServer"
        }, verify=False)
        data = response.json()
        if 'valid' in data and data['valid'] == True:
            return self.verify_scope(request, data)
        return False

    def verify_scope(self, request, data):
        return 'scope' in data and data['scope'] == request.path[1:]


if __name__ == '__main__':
    port = 9002
    app = AuthServiceApplication()
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('certs/domain_srv.crt', 'certs/domain_srv.key')
    web.run_app(app, port=port, ssl_context=ssl_context)
