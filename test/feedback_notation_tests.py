import datetime
import json


import jwt
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application
from tortoise import Tortoise

from app.handlers.base_auth_handler import SECRET_KEY
from app.handlers.feedback_notation_handler import FeedBackNotationHandler
from app.models import User, Feedback, FeedbackNotation
from test.db_test_config import init_inmemory_db


class TestFeedBackNotationHandlerIntegration(AsyncHTTPTestCase):
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
            (r"/feedback/([0-9]+)/notations", FeedBackNotationHandler),
        ])

    async def _create_feedback(self):
        """Create a feedback for testing notations"""
        return await Feedback.create(user=self.user, note="Test note", rating=5)

    def _generate_token(self, user):
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @gen_test
    async def test_post_valid_notation(self):
        feedback = await self._create_feedback()
        token = self._generate_token(self.user)
        body = json.dumps({"value": 1})

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{feedback.id}/notations"),
            method="POST",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )

        self.assertEqual(response.code, 201)
        data = json.loads(response.body)





        # Assert DB record exists
        notation = await FeedbackNotation.get(  user=self.user, feedback_id=feedback.id)
        self.assertEqual(notation.value, 1)

    @gen_test
    async def test_post_invalid_notation(self):
        feedback = await self._create_feedback()
        token = self._generate_token(self.user)
        body = json.dumps({"value": 10})  # invalid value

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{feedback.id}/notations"),
            method="POST",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )

        self.assertNotEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertIn("error", data)

    @gen_test
    async def test_post_missing_auth(self):
        feedback = await self._create_feedback()
        body = json.dumps({"value": 1})

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{feedback.id}/notations"),
            method="POST",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 401)
        data = json.loads(response.body)
        self.assertIn("error", data)

        ## patch

    @gen_test
    async def test_patch_update_notation(self):
        feedback = await self._create_feedback()
        token = self._generate_token(self.user)

        notation = await FeedbackNotation.create(user=self.user, feedback=feedback, value=3)
        body = json.dumps({"value": -1})  # new value

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{feedback.id}/notations"),
            method="PATCH",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )

        self.assertEqual(response.code, 200)
        data = json.loads(response.body)



        updated = await FeedbackNotation.get(id=notation.id)
        self.assertEqual(updated.value, -1)

    @gen_test
    async def test_patch_invalid_value(self):
        feedback = await self._create_feedback()
        token = self._generate_token(self.user)

        notation = await FeedbackNotation.create(user=self.user, feedback=feedback, value=3)
        body = json.dumps({"value": 999})  # invalid value

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{feedback.id}/notations"),
            method="PATCH",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )

        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertIn("error", data)

    @gen_test
    async def test_patch_missing_auth(self):
        feedback = await self._create_feedback()
        notation = await FeedbackNotation.create(user=self.user, feedback=feedback, value=3)
        body = json.dumps({"value": 1})

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{feedback.id}/notations"),
            method="PATCH",
            body=body,
            raise_error=False
        )

        self.assertEqual(response.code, 401)
        data = json.loads(response.body)
        self.assertIn("Unauthorized", data.get("log_message", "Unauthorized"))

    @gen_test
    async def test_patch_feedback_not_found(self):
        token = self._generate_token(self.user)
        body = json.dumps({"value": -1})

        response = await self.http_client.fetch(
            self.get_url("/feedback/999999/notations"),
            method="PATCH",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )

        self.assertEqual(response.code, 404)
        data = json.loads(response.body)
        self.assertIn("error", data)

    ## get summary

    @gen_test
    async def test_get_summary_with_notations(self):
        feedback = await self._create_feedback()
        token = self._generate_token(self.user)

        # create notations
        await FeedbackNotation.create(user=self.user, feedback=feedback, value=1)
        another_user = await User.create(username="otheruser", password="pw")
        await FeedbackNotation.create(user=another_user, feedback=feedback, value=-1)

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{feedback.id}/notations"),
            method="GET",
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )

        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertEqual(int(data["feedback_id"]), feedback.id)
        self.assertEqual(data["positive_notations"], 1)
        self.assertEqual(data["negative_notations"], 1)
        self.assertEqual(data["user_notation"], 1)

    @gen_test
    async def test_get_summary_no_notations(self):
        feedback = await self._create_feedback()
        token = self._generate_token(self.user)

        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{feedback.id}/notations"),
            method="GET",
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )

        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertEqual(data["positive_notations"], 0)
        self.assertEqual(data["negative_notations"], 0)
        self.assertEqual(data["user_notation"], 0)
