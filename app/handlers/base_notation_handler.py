import tornado
from app.handlers.base_auth_handler import BaseAuthHandler
from app.service.notation_service import (
    validate_notation_value,
    create_notation,
    update_notation,
    get_notation_summary,
)
import logging


class BaseNotationHandler(BaseAuthHandler):
    """Generic notation handler for any notation model"""

    notation_model = None  # subclass should set this

    async def handle_notation(self, object_id, service_method):
        self.require_auth()
        try:
            data = tornado.escape.json_decode(self.request.body)
        except ValueError:
            self.set_status(400)
            return self.write({"error": "Invalid JSON body"})

        value = data.get("value")
        ok, error, status = await validate_notation_value(value)
        if not ok:
            self.set_status(status)
            return self.write(error)

        resp, status = await service_method(self.notation_model, self.current_user, object_id, value)
        self.set_status(status)
        self.write(resp)

    async def post(self, object_id):
        await self.handle_notation(object_id, create_notation)

    async def patch(self, object_id):
        await self.handle_notation(object_id, update_notation)

    async def get(self, object_id):
        self.require_auth()
        resp, status = await get_notation_summary(self.notation_model, self.current_user, object_id)
        self.set_status(status)
        self.write(resp)
