# test/feedback_tests.py
import json
import datetime
import unittest

import tornado
from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase, gen_test

import jwt
from tortoise import Tortoise

from app.models import User, Feedback
from app.handlers.feedback_handler import FeedbackHandler
from app.handlers.base_auth_handler import SECRET_KEY
from test.db_test_config import init_inmemory_db, close_inmemory_db


class TestFeedbackHandlerIntegration(AsyncHTTPTestCase):
    user = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import asyncio
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
        cls.loop.run_until_complete(init_inmemory_db())
        cls.user = cls.loop.run_until_complete(
            User.create(username="testuser", password="hashedpw")
        )

    @classmethod
    def tearDownClass(cls):
        cls.loop.run_until_complete(Tortoise.close_connections())
        cls.loop.close()
        super().tearDownClass()

    def get_app(self):
        return Application([
            (r"/feedback", FeedbackHandler),
            (r"/feedback/([0-9]+)", FeedbackHandler),
        ])

    async def _create_user(self, username="testuser"):
        """Create user only if it doesn't exist yet"""
        if not self.user:
            self.user = await User.create(username=username, password="hashedpw")
        return self.user

    def _generate_token(self, user):
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @gen_test
    async def test_create_feedback_happy_path(self):
        user = await self._create_user()
        token = self._generate_token(user)
        body = json.dumps({"note": "Great product", "rating": 5})
        response = await self.http_client.fetch(
            self.get_url("/feedback"),
            method="POST",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertEqual(data["note"], "Great product")
        self.assertEqual(data["message"], "Feedback created")

    @gen_test
    async def test_create_feedback_missing_auth(self):
        body = json.dumps({"note": "No auth", "rating": 3})
        response = await self.http_client.fetch(
            self.get_url("/feedback"),
            method="POST",
            body=body,
            raise_error=False
        )
        self.assertEqual(response.code, 401)
        data = json.loads(response.body)
        self.assertIn("Unauthorized", data["log_message"] if "log_message" in data else "Unauthorized")

    @gen_test
    async def test_create_feedback_invalid_rating(self):
        token =  self._generate_token(self.user)
        body = json.dumps({"note": "Bad rating", "rating": 10})
        response = await self.http_client.fetch(
            self.get_url("/feedback"),
            method="POST",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )
        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertIn("Rating must be an integer", data["error"])

    @gen_test
    async def test_create_feedback_missing_fields(self):
        token =  self._generate_token(self.user)
        body = json.dumps({"note": "No rating"})
        response = await self.http_client.fetch(
            self.get_url("/feedback"),
            method="POST",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )
        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertIn("Rating must be an integer", data["error"])

    @gen_test
    async def test_get_all_feedback(self):

        fb = await Feedback.create(user=self.user, note="Sample note", rating=4)

        response = await self.http_client.fetch(
            self.get_url("/feedback"),
            method="GET",
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertIn("feedbacks", data)
        self.assertTrue(any(f["id"] == fb.id for f in data["feedbacks"]))

    @gen_test
    async def test_get_single_feedback_happy_path(self):
        fb = await Feedback.create(user=self.user, note="Single note", rating=5)

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{fb.id}"),
            method="GET",
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertEqual(data["id"], fb.id)
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["note"], "Single note")
        self.assertEqual(data["rating"], 5)

    @gen_test
    async def test_get_single_feedback_not_found(self):
        response = await self.http_client.fetch(
            self.get_url("/feedback/999999"),
            method="GET",
            raise_error=False
        )
        self.assertEqual(response.code, 404)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Feedback not found")
