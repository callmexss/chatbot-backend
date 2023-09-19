from django.test import TestCase
from rest_framework.test import APIClient

# Create your tests here.


class MessageTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_echo_message(self):
        response = self.client.post(
            "/chat/echo/", {"content": "Hello, world!"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Hello, world!")
