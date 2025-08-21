# app/handlers/comment_notation_handler.py
import tornado

from app.service.notation_service import create_notation, update_notation, get_notation_summary, validate_notation_value

from app.handlers.base_auth_handler import BaseAuthHandler
from app.models import CommentNotation, Comment


class CommentNotationHandler(BaseAuthHandler):
    async def post(self, comment_id):
        self.require_auth()

        # Validate the notation value
        data = tornado.escape.json_decode(self.request.body)
        value = data.get("value")

        ok, error, status = await validate_notation_value(value)
        if not ok:
            self.set_status(status)
            self.write(error)
            return
        res, status = await create_notation(CommentNotation, self.current_user, comment_id, value)
        self.set_status(status)
        self.write(res)

    async def patch(self, comment_id):
        self.require_auth()
        data = tornado.escape.json_decode(self.request.body)
        value = data.get("value")

        ok, error, status = await validate_notation_value(value)
        if not ok:
            self.set_status(status)
            self.write(error)
            return
        res, status = await update_notation(CommentNotation, self.current_user, comment_id, value)
        self.set_status(status)
        self.write(res)

    # get summary of notations for a comment
    async def get(self, comment_id):
        self.require_auth()
        # Validate comment_id
        comment = await Comment.get_or_none(id=comment_id)
        if not comment:
            self.set_status(404)
            self.write({"error": "Comment not found"})
            return
        res, status = await get_notation_summary(CommentNotation, self.current_user, comment_id)
        self.set_status(status)
        self.write(res)
