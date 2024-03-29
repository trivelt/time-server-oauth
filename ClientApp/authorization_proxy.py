import asyncio
import logging
import requests_async
from aiohttp import web

from async_utils import wait_for
from config import AppConfig

logger = logging.getLogger(__name__)


class AuthorizationProxy:
    AUTH_SERVER_URL = "https://127.0.0.1:9001"
    AUTHORIZE_ENDPOINT = AUTH_SERVER_URL + "/authorize"
    GET_TOKEN_ENDPOINT = AUTH_SERVER_URL + "/get_token"
    RECEIVE_TOKEN_TIMEOUT_SEC = 5

    def __init__(self):
        self.token_events = dict()
        self.token_values = dict()

    async def retrieve_token(self, scope):
        try:
            received_token_event = self._create_token_event(scope)
            await self.send_authorization_code_request(scope)
            await wait_for(received_token_event, AuthorizationProxy.RECEIVE_TOKEN_TIMEOUT_SEC)
            if scope not in self.token_values:
                return None
            token = self.token_values[scope].pop()
        except requests_async.exceptions.ConnectionError:
            logger.exception("Cannot connect to the auth server")
            return None
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
        return await requests_async.get(AuthorizationProxy.AUTHORIZE_ENDPOINT, params=json_dict, verify=False)

    async def send_token_request(self, authorization_code):
        json_dict = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_secret": AppConfig.CLIENT_SECRET,
            "redirect_uri": AppConfig.AUTH_CALLBACK_URL
        }
        return await requests_async.get(AuthorizationProxy.GET_TOKEN_ENDPOINT, params=json_dict, verify=False)

    async def handle_auth_callback(self, request):
        scope = request.query.get('scope', None)
        code = request.query.get('code', None)
        if scope is None or code is None:
            logger.error("Received invalid auth callback request: %s", request.query)
            self._set_invalid_token(scope)
        else:
            try:
                response = await self.send_token_request(code)
                response.raise_for_status()
                response_data = response.json()
                token = response_data['access_token']
                self._push_into_dict(self.token_values, scope, token)
            except ValueError:
                logger.exception("Could not receive valid token message")
                self._set_invalid_token(scope)
            except KeyError:
                logger.exception("Invalid token message with missing parameter")
                self._set_invalid_token(scope)
            except requests_async.exceptions.HTTPError:
                logger.exception("Received error message from auth service")
                self._set_invalid_token(scope)

        if scope:
            self.token_events[scope].pop().set()
        return web.json_response({}, status=200)

    def _set_invalid_token(self, scope):
        self._push_into_dict(self.token_values, scope, None)
