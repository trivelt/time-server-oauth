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
            dict_object[key].insert(0, value)

    async def send_authorization_code_request(self, scope):
        json_dict = {
            "response_type": "code",
            "client_id": AppConfig.CLIENT_ID,
            "scope": scope,
            "redirect_uri": AppConfig.AUTH_CALLBACK_URL
        }
        return await requests_async.get(AuthorizationProxy.AUTHORIZE_ENDPOINT, params=json_dict)

    async def send_token_request(self, authorization_code):
        json_dict = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_secret": AppConfig.CLIENT_SECRET,
            "redirect_uri": AppConfig.AUTH_CALLBACK_URL
        }
        return await requests_async.get(AuthorizationProxy.GET_TOKEN_ENDPOINT, params=json_dict)

    async def handle_auth_callback(self, request):
        scope = request.query.get('scope', None)
        code = request.query.get('code', None)
        if scope is None or code is None:
            print("Error: Received invalid auth callback request: " + str(request.query))
            self._set_invalid_token(scope)
        else:
            try:
                response = await self.send_token_request(code)
                response.raise_for_status()
                response_data = response.json()
                token = response_data['access_token']
                self._push_into_dict(self.token_values, scope, token)
            except ValueError as exc:
                print("Error: Could not receive valid token message: " + str(exc))
                self._set_invalid_token(scope)
            except KeyError as exc:
                print("Error: Invalid token message with missing parameter: " + str(exc))
                self._set_invalid_token(scope)
            except requests_async.exceptions.HTTPError as exc:
                print("Error: Received error message from auth service: " + str(exc))
                self._set_invalid_token(scope)

        self.token_events[scope].pop().set()
        return web.json_response({}, status=200)

    def _set_invalid_token(self, scope):
        self._push_into_dict(self.token_values, scope, None)
