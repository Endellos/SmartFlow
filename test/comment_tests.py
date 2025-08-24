# test/comment_tests.py
import json
import datetime

from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase, gen_test
import jwt

from app.models import User, Feedback, Comment
from app.handlers.comment_handler import CommentHandler, SingleCommentHandler, FeedbackCommentsHandler
from app.handlers.base_auth_handler import SECRET_KEY
from test.db_test_config import init_inmemory_db, close_inmemory_db


class TestCommentHandlerIntegration(AsyncHTTPTestCase):
    user = None
    feedback = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import asyncio
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

        async def _init():
            await init_inmemory_db()
            cls.user = await User.create(username="testuser", password="hashedpw")
            cls.feedback = await Feedback.create(
                user=cls.user, note="Seed feedback", rating=5
            )

        cls.loop.run_until_complete(_init())

    @classmethod
    def tearDownClass(cls):
        cls.loop.run_until_complete(close_inmemory_db())
        cls.loop.close()
        super().tearDownClass()

    def get_app(self):
        return Application([
            (r"/comments", CommentHandler),
            (r"/comments/([0-9]+)", SingleCommentHandler),
            (r"/feedback/([0-9]+)/comments", FeedbackCommentsHandler)
        ])
    async def _create_user_and_feedback(self):
        user = await User.create(username="testuser", password="hashedpw")
        fb = await Feedback.create(user=user, note="Great product", rating=5)
        return user, fb


    def _generate_token(self, user):
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # ------------------
    # POST /comments
    # ------------------

    @gen_test
    async def test_create_comment_happy_path(self):
        token = self._generate_token(self.user)
        body = json.dumps({"content": "Nice feedback!", "feedback_id": self.feedback.id})
        response = await self.http_client.fetch(
            self.get_url("/comments"),
            method="POST",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertEqual(data["text"], "Nice feedback!")
        self.assertEqual(data["message"], "Comment created")

    @gen_test
    async def test_create_comment_missing_auth(self):
        body = json.dumps({"content": "No auth", "feedback_id": self.feedback.id})
        response = await self.http_client.fetch(
            self.get_url("/comments"),
            method="POST",
            body=body,
            raise_error=False
        )
        self.assertEqual(response.code, 401)
        data = json.loads(response.body)
        self.assertIn("Unauthorized", data.get("error", "Unauthorized"))

    @gen_test
    async def test_create_comment_missing_content(self):
        token = self._generate_token(self.user)
        body = json.dumps({"feedback_id": self.feedback.id})
        response = await self.http_client.fetch(
            self.get_url("/comments"),
            method="POST",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )
        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Comment content is required")

    @gen_test
    async def test_create_comment_feedback_not_found(self):
        token = self._generate_token(self.user)
        body = json.dumps({"content": "Ghost feedback", "feedback_id": 999999})
        response = await self.http_client.fetch(
            self.get_url("/comments"),
            method="POST",
            body=body,
            headers={"Authorization": f"Bearer {token}"},
            raise_error=False
        )
        self.assertEqual(response.code, 404)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Feedback not found")

        # ------------------ GET /comments/{id} ------------------

    @gen_test
    async def test_get_single_comment_happy_path(self):
        comment = await Comment.create(
            user=self.user, feedback=self.feedback, content="Seed comment"
        )
        response = await self.http_client.fetch(
            self.get_url(f"/comments/{comment.id}"),
            method="GET",
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertEqual(data["id"], comment.id)
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["feedback_id"], self.feedback.id)
        self.assertEqual(data["content"], "Seed comment")

    @gen_test
    async def test_get_single_comment_not_found(self):
        response = await self.http_client.fetch(
            self.get_url("/comments/999999"),
            method="GET",
            raise_error=False
        )
        self.assertEqual(response.code, 404)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Comment not found")

        # ------------------ GET /feedback/{id}/comments ------------------

    @gen_test
    async def test_get_all_comments_for_feedback(self):
        # Add some comments
        await Comment.create(user=self.user, feedback=self.feedback, content="Another comment")
        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{self.feedback.id}/comments"),
            method="GET",
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertGreaterEqual(len(data.get("comments", [])), 1)

    @gen_test
    async def test_get_all_comments_for_feedback_empty(self):
        # Create a new feedback with no comments
        empty_feedback = await Feedback.create(user=self.user, note="Empty feedback", rating=3)
        response = await self.http_client.fetch(
            self.get_url(f"/feedback/{empty_feedback.id}/comments"),
            method="GET",
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertEqual(data.get("comments", []), [])

    @gen_test
    async def test_get_all_comments_for_nonexistent_feedback(self):
        response = await self.http_client.fetch(
            self.get_url("/feedback/999999/comments"),
            method="GET",
            raise_error=False
        )
        self.assertEqual(response.code, 404)
        data = json.loads(response.body)
        self.assertEqual(data["error"], "Feedback not found")