from tortoise import fields, models
from tortoise.models import Model


# -----------------------------
# Abstract base for notations
# -----------------------------
class Notation(models.Model):
    user = fields.ForeignKeyField('models.User', related_name='notations')
    value = fields.IntField(choices=[-1, 0, 1])  # -1, 0, 1

    class Meta:
        abstract = True  # will not create a table for this


# -----------------------------
# User model
# -----------------------------
class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)  # encrypted password


# -----------------------------
# Feedback model
# -----------------------------
class Feedback(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='feedbacks')
    rating = fields.IntField(choices=[1, 2, 3, 4, 5])  # 1-5
    note = fields.TextField(null=True)  # optional


# -----------------------------
# Comment model
# -----------------------------
class Comment(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='comments')
    feedback = fields.ForeignKeyField('models.Feedback', related_name='comments')
    content = fields.TextField()


# -----------------------------
# Notation subtypes
# -----------------------------
class FeedbackNotation(Notation):
    feedback = fields.ForeignKeyField('models.Feedback', related_name='notations')
    user = fields.ForeignKeyField('models.User', related_name='feedback_notations')


class CommentNotation(Notation):
    comment = fields.ForeignKeyField('models.Comment', related_name='notations')
    user = fields.ForeignKeyField('models.User', related_name='comment_notations')
