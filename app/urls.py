

from app.handlers.comment_handler import CommentHandler
from app.handlers.comment_notation_handler import CommentNotationHandler
from app.handlers.feedback_handler import FeedbackHandler
from app.handlers.feedback_notation_handler import FeedBackNotationHandler
from app.handlers.health_handler import HealthCheckHandler
from app.handlers.user_handler import RegisterHandler, LoginHandler

urlpatterns = [
    (r"/", HealthCheckHandler),
    (r"/api/register", RegisterHandler),
    (r"/api/login", LoginHandler),
    (r"/api/feedback", FeedbackHandler),
    (r"/api/feedback/([0-9]+)", FeedbackHandler),
    (r"/api/comment", CommentHandler),
    (r"/api/comment/([0-9]+)", CommentHandler),  # comment_id
    (r"/api/feedback/([0-9]+)/comments", CommentHandler),  # feedback_id
    # Feedback notations
    (r"/api/feedback/([0-9]+)/notations", FeedBackNotationHandler),
    (r"/api/feedback/([0-9]+)/notations/summary", FeedBackNotationHandler),

    # Comment notations
    (r"/api/comment/([0-9]+)/notations", CommentNotationHandler),
    (r"/api/comment/([0-9]+)/notations/summary", CommentNotationHandler),
]


