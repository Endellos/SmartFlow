import tornado
from app.handlers.base_auth_handler import BaseAuthHandler
from app.models import FeedbackNotation
from app.service.notation_service import (
    validate_notation_value,
    create_notation,
    update_notation,
    get_notation_summary,
)


class FeedBackNotationHandler(BaseAuthHandler):
    async def post(self, feedback_id):
        self.require_auth()
        data = tornado.escape.json_decode(self.request.body)
        value = data.get("value")


        ok, error, status = await validate_notation_value(value)
        if not ok:
            self.set_status(status)
            self.write(error)
            return

        resp, status = await create_notation(FeedbackNotation, self.current_user, feedback_id, value)
        self.set_status(status)
        self.write(resp)

    async def patch(self, feedback_id):
        self.require_auth()
        data = tornado.escape.json_decode(self.request.body)
        value = data.get("value")


        ok, error, status = await validate_notation_value(value)
        if not ok:
            self.set_status(status)
            self.write(error)
            return

        resp, status = await update_notation(FeedbackNotation, self.current_user, feedback_id, value)
        self.set_status(status)
        self.write(resp)
        return

    # get summary of notations for a feedback
    async def get(self, feedback_id):
        self.require_auth()
        resp, status = await get_notation_summary(FeedbackNotation, self.current_user, feedback_id)
        self.set_status(status)
        self.write(resp)
