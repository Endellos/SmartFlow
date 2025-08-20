from  app.handlers.user_handlers import RegisterHandler, LoginHandler

urlpatterns = [
    (r"/api/register", RegisterHandler),
    (r"/api/login", LoginHandler),

]