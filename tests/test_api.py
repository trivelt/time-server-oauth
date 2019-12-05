import requests
from unittest import TestCase
from datetime import datetime

CURRENT_TIME = "/current_time"
EPOCH_TIME = "/epoch_time"
RESOURCES = (CURRENT_TIME, EPOCH_TIME)


class TestClientApi(TestCase):
    def send_get(self, endpoint):
        return requests.get("http://127.0.0.1:9000" + endpoint)

    def test_currentTimeEndpoint_shouldReturnTimeString(self):
        response = self.send_get("/current_time")
        returned_json = response.json()

        self.assertTrue('time' in returned_json)
        try:
            date_format = "%Y-%m-%d %H:%M:%S.%f"
            datetime.strptime(returned_json['time'], date_format)
        except:
            raise AssertionError("Incorrect date: " + str(returned_json))

    def test_epochTimeEndpoint_shouldReturnUnixTimeNumber(self):
        response = self.send_get("/epoch_time")
        returned_json = response.json()

        self.assertTrue('time' in returned_json)
        self.assertTrue(isinstance(returned_json['time'], int))


class TestResourceServerApi(TestCase):
    def send_get(self, endpoint):
        return requests.get("https://127.0.0.1:9002" + endpoint, verify=False)

    def test_timeEndpoints_shouldReturnUnauthorizedError_WhenValidTokenIsNotProvided(self):
        for resource in RESOURCES:
            with self.subTest():
                response = self.send_get(resource)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.json()['error'], "Token authorization failed")
