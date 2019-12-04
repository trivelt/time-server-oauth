from aiohttp import web
import requests_async
import jwt
from time import time
from databases.auth_codes_database import AuthCodesDatabase
from databases.clients_database import ClientsDatabase
from utils import random_string


class AuthServiceApplication(web.Application):
    TOKEN_EXPIRATION_TIME_SEC = 5
    AUTH_TOKEN_LENGTH = 32

    def __init__(self):
        web.Application.__init__(self)
        self.configure_routes()
        self.jwt_secret = random_string(length=16)
        self.codes_database = AuthCodesDatabase()
        self.clients_database = ClientsDatabase()

    def configure_routes(self):
        self.router.add_route('GET', '/authorize', self.authorize)
        self.router.add_route('GET', '/get_token', self.get_token)
        self.router.add_route('GET', '/validate_token', self.validate_token)

    async def authorize(self, request):
        callback_url = request.query['redirect_uri']
        client_id = request.query.get('client_id', None)
        if not client_id or not self.clients_database.client_exists(client_id):
            await requests_async.get(callback_url, json={"error": "invalid request"})

        scope = request.query['scope']
        response_params = {
            "code": self.generate_auth_code(scope, client_id),
            "scope": scope
        }
        await requests_async.get(callback_url, params=response_params)
        return web.json_response({}, status=200)

    async def get_token(self, request):
        auth_code = request.query.get('code', None)
        if not self.codes_database.is_valid(auth_code):
            return web.json_response({"error": "invalid request"}, status=400)

        client_id = self.codes_database.get_client_id(auth_code)
        client_secret = request.query.get('client_secret', None)
        if not client_secret or not self.validate_client_secret(client_id, client_secret):
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

    def validate_client_secret(self, client_id, client_secret):
        return self.clients_database.verify_client_secret(client_id, client_secret)

    def generate_auth_code(self, scope, client_id):
        auth_code = random_string(length=AuthServiceApplication.AUTH_TOKEN_LENGTH)
        self.codes_database.add(auth_code, scope, client_id)
        return auth_code

    def generate_token(self, scope):
        jwt_payload = {
            "iss": "TestAuthService",
            "sub": scope,
            "aud": "TimeServer",
            "exp": int(time()) + AuthServiceApplication.TOKEN_EXPIRATION_TIME_SEC
        }
        return jwt.encode(jwt_payload, self.jwt_secret, algorithm='HS256').decode("utf-8")

    async def validate_token(self, request):
        encoded_token = request.query.get('access_token', None)
        audience = request.query.get('audience', None)
        if not (audience and encoded_token):
            print("Error: Could not validate token: missing parameter")
            return web.json_response({"error": "missing parameter"}, status=400)

        try:
            decoded_token = jwt.decode(encoded_token, self.jwt_secret, audience=audience, algorithms=['HS256'])
            validation_result = decoded_token["exp"] > time()
            scope = decoded_token["sub"]
        except Exception as exc:
            print("Error: " + str(exc))
            validation_result = False
            scope = None
        return web.json_response({"valid": validation_result,
                                  "scope": scope}, status=200)


if __name__ == '__main__':
    port = 9001
    app = AuthServiceApplication()
    web.run_app(app, port=port)
