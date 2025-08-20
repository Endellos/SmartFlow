import json

from unittest.mock import AsyncMock, patch

from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase, gen_test

from app.handlers.user_handler import RegisterHandler

class TestRegisterHandler(AsyncHTTPTestCase):

    def get_app(self):
        return Application([
            (r"/register", RegisterHandler),
        ])

    def setUp(self):
        super().setUp()
        # Patch User methods for all tests
        patcher_get = patch("app.handlers.user_handler.User.get_or_none", new_callable=AsyncMock)
        self.mock_get = patcher_get.start()
        self.addCleanup(patcher_get.stop)

        patcher_create = patch("app.handlers.user_handler.User.create", new_callable=AsyncMock)
        self.mock_create = patcher_create.start()
        self.addCleanup(patcher_create.stop)


    @gen_test
    async def test_register_missing_fields(self):
        body = json.dumps({"username": "useronly"})  # missing password
        response = await self.http_client.fetch(
            self.get_url("/register"),
            method="POST",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertIn("required", data["error"])

    @gen_test
    async def test_register_username_exists(self):
        # Simulate existing user
        self.mock_get.return_value = AsyncMock(id=1, username="existinguser")

        body = json.dumps({"username": "existinguser", "password": "pass"})
        response = await self.http_client.fetch(
            self.get_url("/register"),
            method="POST",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Username already exists")
