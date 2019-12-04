import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch
from aiohttp.test_utils import unittest_run_loop

from auth_service import AuthServiceApplication

CORRECT_AUTH_CODE = "AUTH-CODE"


class TestAuthService(TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.service = AuthServiceApplication()

    @patch("auth_service.random_string", MagicMock(return_value=CORRECT_AUTH_CODE))
    def test_generateAuthCode_shouldStoreAuthCodeInDatabase(self):
        # Given
        scope = "SomeScope"
        client_id = 123
        self.service.codes_database = MagicMock()

        # When
        auth_code = self.service.generate_auth_code(scope, client_id)

        # Then
        self.service.codes_database.add.assert_called_once_with(CORRECT_AUTH_CODE, scope, client_id)

    @patch("aiohttp.web.json_response")
    @unittest_run_loop
    async def test_getToken_shouldReturnErrorResponse_WhenAuthCodeIsInvalid(self, json_response):
        # Given
        request = MagicMock()
        self.service.codes_database = MagicMock()
        self.service.codes_database.is_valid.return_value = False

        # When
        response = await self.service.get_token(request)

        # Then
        self.assertEqual(response, json_response.return_value)
        json_response.assert_called_once_with({"error": "invalid request"}, status=400)
