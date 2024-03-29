import logging
from aiohttp import web

from authorization_proxy import AuthorizationProxy
from time_server_proxy import TimeServerProxy
from config import AppConfig


class ClientWebApplication(web.Application):
    def __init__(self):
        web.Application.__init__(self)
        self.auth_proxy = AuthorizationProxy()
        self.configure_routes()

    def configure_routes(self):
        self.router.add_route('GET', '/current_time', self.handle_time_request)
        self.router.add_route('GET', '/epoch_time', self.handle_time_request)
        self.router.add_route('GET', AppConfig.AUTH_CALLBACK, self.auth_proxy.handle_auth_callback)

    async def handle_time_request(self, request):
        scope = request.path[1:]
        token = await self.auth_proxy.retrieve_token(scope)
        if not token:
            return web.json_response({"error": "authorization error"}, status=500)
        status_code, time_data = await TimeServerProxy.get_time(scope, token)
        return web.json_response(time_data, status=status_code)


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s")
    app = ClientWebApplication()
    web.run_app(app, port=AppConfig.PORT)
