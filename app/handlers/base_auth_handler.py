# app/handlers/base.py
import os

import jwt
from tornado.web import RequestHandler, HTTPError

from dotenv import load_dotenv
import logging

from app.models import User

# configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    import secrets

    SECRET_KEY = secrets.token_urlsafe(32)
    logging.warning("WARNING: Using auto-generated SECRET_KEY for dev only!")


class BaseAuthHandler(RequestHandler):
    """Base handler with JWT auth and automatic user fetching"""

    async def prepare(self):
        """Called before every request; decodes JWT and sets self.current_user_obj"""
        self.current_user_obj = None  # default

        auth = self.request.headers.get("Authorization")

        if not auth or not auth.startswith("Bearer "):
            return  # no token, self.current_user_obj stays None

        token = auth.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            user_id = payload.get("sub")

            if user_id:
                self.current_user_obj = await User.get_or_none(id=int(user_id))
        except jwt.ExpiredSignatureError:
            logging.warning("JWT token expired")
            return  # invalid token, leave current_user_obj as None
        except jwt.InvalidTokenError as e:
            logging.error("Invalid JWT token: %s", e)
            return

    @property
    def current_user(self):
        """Returns the authenticated User object, or None"""
        return self.current_user_obj

    def require_auth(self):
        """Raise 401 if user not authenticated. Add this to the beginning of any handler method that requires auth."""
        if not self.current_user:
            raise HTTPError(401, "Unauthorized")

    def write_error(self, status_code, **kwargs):
        """Return JSON for all errors instead of HTML"""
        self.set_header("Content-Type", "application/json")
        if "exc_info" in kwargs:
            exc = kwargs["exc_info"][1]
            self.finish({"error": str(exc)})
        else:
            self.finish({"error": self._reason})
