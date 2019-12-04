from aiohttp import web
import requests_async
import random
import string
import jwt
from time import time
from auth_codes_database import AuthCodesDatabase


class AuthServiceApplication(web.Application):
    TOKEN_EXPIRATION_TIME_SEC = 5
    AUTH_TOKEN_LENGTH = 32

    def __init__(self):
        web.Application.__init__(self)
        self.configure_routes()
        self.jwt_secret = self._random_string(length=16)
        self.codes_database = AuthCodesDatabase()

    def configure_routes(self):
        self.router.add_route('GET', '/authorize', self.authorize)
        self.router.add_route('GET', '/get_token', self.get_token)
        self.router.add_route('GET', '/validate_token', self.validate_token)

    async def authorize(self, request):
        self.validate_client(request)
        callback_url = request.query['redirect_uri']
        scope = request.query['scope']
        response_params = {
            "code": self.generate_auth_code(scope),
            "scope": scope
        }
        await requests_async.get(callback_url, params=response_params)
        return web.json_response({}, status=200)

    async def get_token(self, request):
        auth_code = request.query['code']
        if not self.codes_database.is_valid(auth_code):
            return web.json_response({"error": "invalid request"}, status=400)

        scope = self.codes_database.get_scope(auth_code)
        self.codes_database.remove(auth_code)
        response_data = {
            "access_token": self.generate_token(scope),
            "token_type": "bearer",
            "expires_in": AuthServiceApplication.TOKEN_EXPIRATION_TIME_SEC,
            "scope": scope
        }
        return web.json_response(response_data, status=200)

    def validate_client(self, request):
        pass
        # Validate only id
        # Validate secret

    def generate_auth_code(self, scope):
        auth_code = self._random_string(length=AuthServiceApplication.AUTH_TOKEN_LENGTH)
        self.codes_database.add(auth_code, scope)
        return auth_code

    def _random_string(self, length):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def generate_token(self, scope):
        jwt_payload = {
            "iss": "TestAuthService",
            "sub": scope,
            "aud": "TimeServer",
            "exp": int(time()) + AuthServiceApplication.TOKEN_EXPIRATION_TIME_SEC
        }
        return jwt.encode(jwt_payload, self.jwt_secret, algorithm='HS256').decode("utf-8")

    async def validate_token(self, request):
        return web.json_response({}, status=200)


if __name__ == '__main__':
    port = 9001
    app = AuthServiceApplication()
    web.run_app(app, port=port)
