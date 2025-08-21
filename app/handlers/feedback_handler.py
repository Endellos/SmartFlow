import tornado

from app.handlers.base_auth_handler import BaseAuthHandler
from app.models import Feedback


class FeedbackHandler(BaseAuthHandler):
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

    async def get(self, feedback_id=None):
        """Get all feedbacks or a single feedback by id, both are lazy loaded if u need the comments call `methodname`.
       """
        if feedback_id:
            feedback = await Feedback.get_or_none(id=feedback_id).prefetch_related('user')
            if not feedback:
                self.set_status(404)
                self.write({"error": "Feedback not found"})
                return
            self.write({
                "id": feedback.id,
                "user_id": feedback.user.id,
                "username": feedback.user.username,  # for display purpose
                "note": feedback.note,
                "rating": feedback.rating,

            })
        else:
            all_feedbacks = await Feedback.all().prefetch_related('user')
            feedback_list = [{
                "id": fb.id,
                "user_id": fb.user.id,
                "username": fb.user.username,  # for display purpose
                "note": fb.note,
                "rating": fb.rating
            } for fb in all_feedbacks]
            self.write({"feedbacks": feedback_list})
