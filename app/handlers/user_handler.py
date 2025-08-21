# app/handlers/user_handler.py
import logging

import tornado.web
import tornado.escape
import jwt
import datetime
from passlib.hash import bcrypt
from tortoise.transactions import in_transaction
from app.models import User
from app.handlers.base_auth_handler import BaseAuthHandler, SECRET_KEY


class RegisterHandler(tornado.web.RequestHandler):
    async def post(self):
        data = tornado.escape.json_decode(self.request.body)
        username = data.get("username")
        password = data.get("password")

        # missing fields validation
        missing = [field for field in ["username", "password"] if not data.get(field)]
        if missing:

            if len(missing) == 1:
                message = f"{missing[0].capitalize()} required"
            else:
                message = " and ".join(missing).capitalize() + " required"
            self.set_status(400)
            self.write({"error": message})
            return

        # existing username validation
        existing = await User.get_or_none(username=username)
        if existing:
            self.set_status(400)
            self.write({"error": "Username already exists"})
            return

        hashed_pw = bcrypt.hash(password)

        async with in_transaction():
            user = await User.create(username=username, password=hashed_pw)

        self.write({"message": "User registered", "id": user.id})


class LoginHandler(tornado.web.RequestHandler):
    async def post(self):
        data = tornado.escape.json_decode(self.request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            self.set_status(400)
            self.write({"error": "Username and password required"})
            return

        user = await User.get_or_none(username=username)
        if not user or not bcrypt.verify(password, user.password):
            self.set_status(401)
            self.write({"error": "Invalid credentials"})
            return

        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        self.write({"token": token})
