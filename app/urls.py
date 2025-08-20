from app.handlers.feedback_handler import FeedbackHandler
from  app.handlers.user_handler import RegisterHandler, LoginHandler

urlpatterns = [
    (r"/api/register", RegisterHandler),
    (r"/api/login", LoginHandler),
    (r"/api/feedback", FeedbackHandler),

]