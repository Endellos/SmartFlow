import tornado

from app.handlers.base_auth_handler import BaseAuthHandler
from app.models import Feedback, Comment


class CommentHandler(BaseAuthHandler):
    async def post(self):
        """Post a comment on a specific feedback"""
        self.require_auth()  # ensures only logged-in users can comment

        data = tornado.escape.json_decode(self.request.body)
        comment_text = data.get("content")
        feedback_id = data.get("feedback_id")

        if not comment_text:
            self.set_status(400)
            self.write({"error": "Comment content is required"})
            return
        # Validate feedback_id
        feedback = await Feedback.get_or_none(id=feedback_id)
        if not feedback:
            self.set_status(404)
            self.write({"error": "Feedback not found"})
            return
        # Create the comment linked to the feedback and current user
        comment = await Comment.create(
            feedback_id=feedback_id,
            content=comment_text,
            user=self.current_user
        )
        self.write({"id": comment.id, "text": comment.content, "message": "Comment created"})

    async def get(self, feedback_id=None, comment_id=None):
        if comment_id:  # GET /comments/{id}
            comment = await Comment.get_or_none(id=comment_id).prefetch_related('user', 'feedback')
            if not comment:
                self.set_status(404)
                self.write({"error": "Comment not found"})
                return
            self.write(
                {
                    "id": comment.id,
                    "user_id": comment.user.id,
                    "username": comment.user.username,  # for display purpose
                    "feedback_id": comment.feedback.id,
                    "content": comment.content
                })

        elif feedback_id:  # GET /feedback/{feedback_id}/comments
            comments = await Comment.filter(feedback_id=feedback_id)
