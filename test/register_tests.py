import asyncio
import json
import unittest

from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase, gen_test
from tortoise import Tortoise
from tortoise.contrib.test import initializer, finalizer

from app.handlers.user_handler import RegisterHandler
from app.models import User
from test.db_test_config import init_inmemory_db


class TestRegisterHandlerIntegration(AsyncHTTPTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
        cls.loop.run_until_complete(init_inmemory_db())

    @classmethod
    def tearDownClass(cls):
        cls.loop.run_until_complete(Tortoise.close_connections())
        cls.loop.close()
        super().tearDownClass()

    def get_app(self):
        return Application([
            (r"/register", RegisterHandler),
        ])
    @gen_test
    async def test_register_happy_path(self):
        body = json.dumps({"username": "newuser", "password": "secret"})
        response = await self.http_client.fetch(
            self.get_url("/register"),
            method="POST",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertEqual(data["message"], "User registered")
        self.assertIsInstance(data["id"], int)

        user = await User.get(id=data["id"])
        self.assertEqual(user.username, "newuser")

    @gen_test
    async def test_register_username_exists(self):
        await User.create(username="existinguser", password="hashedpw")

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

    @gen_test
    async def test_register_missing_fields(self):
        body = json.dumps({"username": "useronly"})
        response = await self.http_client.fetch(
            self.get_url("/register"),
            method="POST",
            body=body,
            raise_error=False
        )
        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertIn("required", data["error"])
