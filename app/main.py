# app/main.py
import tornado.ioloop
import tornado.web
from app.urls import urlpatterns
from db.init_db import init_db# your async DB init


class Application(tornado.web.Application):
    def __init__(self):
        super().__init__(urlpatterns, debug=True)


async def start_app():
    await init_db()  # initialize DB

    print("DB initialized")


if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    print("Server running on http://localhost:8888")

    # Schedule async DB init inside Tornado's IOLoop
    tornado.ioloop.IOLoop.current().add_callback(start_app)

    # Start the IOLoop
    tornado.ioloop.IOLoop.current().start()
