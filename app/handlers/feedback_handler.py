import tornado

from app.handlers.base_handler import BaseHandler
from app.models import Feedback


class FeedbackHandler(BaseHandler):
    async def post(self):
        self.require_auth()  # ensures only logged-in users can post

        data = tornado.escape.json_decode(self.request.body)
        feedback_text = data.get("note")
        rating = data.get("rating")

        if rating is None or not isinstance(rating, int) or not (1 <= rating <= 5):
            self.set_status(400)
            self.write({"error": "Rating must be an integer between 1 and 5"})
            return

        # Use self.current_user directly
        feedback = await Feedback.create(
            user=self.current_user,
            note=feedback_text,
            rating=rating
        )
        self.write({"id": feedback.id, "note": feedback.note, "message": "Feedback created"})
