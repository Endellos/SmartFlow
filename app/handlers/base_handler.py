# app/handlers/base.py
import os

import jwt
from tornado.web import RequestHandler

from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:

    import secrets
    SECRET_KEY = secrets.token_urlsafe(32)
    print("WARNING: Using auto-generated SECRET_KEY for dev only!")

class BaseHandler(RequestHandler):
    """Optional base class for common methods"""

    def get_current_user(self):
        auth = self.request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None
        token = auth.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload  # user info
        except jwt.PyJWTError:
            return None
