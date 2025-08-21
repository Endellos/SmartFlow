import json
import asyncio
import datetime
import unittest

import tornado
from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase, gen_test
from tortoise import Tortoise

from passlib.hash import bcrypt
import jwt

from app.models import User
from app.handlers.user_handler import LoginHandler  # adjust import path
from app.handlers.user_handler import SECRET_KEY     # import your secret key
from test.db_test_config import init_inmemory_db





class TestLoginHandlerIntegration(AsyncHTTPTestCase):
    loop = None

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
            (r"/login", LoginHandler),
        ])

    @gen_test
    async def test_login_happy_path(self):
        # Create test user
        hashed_pw = bcrypt.hash("secret")
        user = await User.create(username="testuser", password=hashed_pw)

        body = json.dumps({"username": "testuser", "password": "secret"})
        response = await self.http_client.fetch(
            self.get_url("/login"),
            method="POST",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertIn("token", data)

        # Decode token to verify payload
        payload = jwt.decode(data["token"], SECRET_KEY, algorithms=["HS256"])
        self.assertEqual(payload["sub"], str(user.id))
        self.assertEqual(payload["username"], user.username)
        self.assertTrue("exp" in payload)

    @gen_test
    async def test_login_wrong_password(self):
        hashed_pw = bcrypt.hash("secret")
        await User.create(username="testuser1", password=hashed_pw)

        body = json.dumps({"username": "testuser1", "password": "wrong"})
        response = await self.http_client.fetch(
            self.get_url("/login"),
            method="POST",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 401)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Invalid credentials")

    @gen_test
    async def test_login_user_not_found(self):
        body = json.dumps({"username": "nouser", "password": "any"})
        response = await self.http_client.fetch(
            self.get_url("/login"),
            method="POST",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 401)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Invalid credentials")

    @gen_test
    async def test_login_missing_fields(self):
        body = json.dumps({"username": "testuser"})
        response = await self.http_client.fetch(
            self.get_url("/login"),
            method="POST",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Username and password required")
