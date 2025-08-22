import tornado


class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"message": "App is running"})