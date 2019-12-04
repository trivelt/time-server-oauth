import requests_async
import asyncio
from aiohttp import web
from config import AppConfig


class AuthorizationProxy:
    AUTH_SERVER_URL = "http://127.0.0.1:9001"
    AUTHORIZE_ENDPOINT = AUTH_SERVER_URL + "/authorize"
    GET_TOKEN_ENDPOINT = AUTH_SERVER_URL + "/get_token"

    def __init__(self):
        self.token_events = dict()
        self.token_values = dict()

    async def retrieve_token(self, scope):
        received_token_event = self._create_token_event(scope)
        await self.send_authorization_code_request(scope)
        await received_token_event.wait()
        token = self.token_values[scope].pop()
        return token

    def _create_token_event(self, scope):
        event = asyncio.Event()
        self._push_into_dict(self.token_events, scope, event)
        return event

    def _push_into_dict(self, dict_object, key, value):
        if key not in dict_object:
            dict_object[key] = [value]
        else:
            self.token_values[key].insert(0, value)

    async def send_authorization_code_request(self, scope):
        json_dict = {"scope": scope, "callback": AppConfig.AUTH_CALLBACK_URL}
        return await requests_async.get(AuthorizationProxy.AUTHORIZE_ENDPOINT, params=json_dict)

    async def send_token_request(self, authorization_code):
        json_dict = {"code": authorization_code, "callback": AppConfig.AUTH_CALLBACK_URL}
        return await requests_async.get(AuthorizationProxy.GET_TOKEN_ENDPOINT, params=json_dict)

    async def handle_auth_callback(self, request):
        request_data = await request.json()
        scope = request_data['scope']
        code = request_data['code']
        response = await self.send_token_request(code)
        response_data = response.json()
        token = response_data['token']

        self._push_into_dict(self.token_values, scope, token)
        self.token_events[scope].pop().set()
        return web.json_response({}, status=200)
