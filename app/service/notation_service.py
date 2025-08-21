### The reson for this file is to have  centralised methods for hnadeling notations as they fellow the same logic with the diffrance
# that they are connected to diffrent entities. All of the validation and logic is the same so we can centralise it here.

from app.models import Feedback, Comment

VALID_VALUES = {-1, 0, 1}


async def get_filed_name(model):
    # figure out the foreign key field name dynamically
    if model.__name__ == "FeedbackNotation":
        fk_field = "feedback_id"
    elif model.__name__ == "CommentNotation":
        fk_field = "comment_id"
    else:
        raise ValueError("Unsupported notation model")
    return fk_field


async def get_owning_model(model):
    # figure out the owning model dynamically
    if model.__name__ == "FeedbackNotation":
        return Feedback
    elif model.__name__ == "CommentNotation":
        return Comment
    else:
        raise ValueError("Unsupported notation model")


async def validate_notation_value(value):
    """Validate notation value."""
    if value is None:
        return False, {"error": "Notation content is required"}, 400
    if value not in VALID_VALUES:
        return False, {"error": "Notation must be -1, 0 or 1"}, 400
    return True, None, None


async def check_existing_notation(model, user, entity_id):
    """Check if a notation already exists for the user and entity."""
    existing = await model.get_or_none(user=user, feedback_id=entity_id)
    if existing:
        return True, existing
    return False, None


async def create_notation(model, user, entity_id, value):
    """
    Generic notation creator for FeedbackNotation and CommentNotation.
    entity_id can be either feedback_id or comment_id depending on the model.
    """
    fk_field = await get_filed_name(model)

    # filter with the right FK
    existing = await model.get_or_none(user=user, **{fk_field: entity_id})
    if existing:
        return {"error": "Can't have more than one notation per entity"}, 400

    notation = await model.create(user=user, **{fk_field: entity_id}, value=value)
    return {"content": notation.value, "message": "Notation created"}, 201


async def update_notation(model, user, entity_id, value):
    """Update an existing notation."""

    fk_field = await get_filed_name(model)
    existing = await model.get_or_none(user=user, **{fk_field: entity_id})
    if not existing:
        return {"error": "Notation not found"}, 404

    existing.value = value
    await existing.save()
    return {"message": "Notation updated", "content": existing.value}, 200


async def get_notation_summary(model, user, entity_id):
    """Return positive, negative counts and the current user's notation."""
    owning_model = await get_owning_model(model)
    entity = await owning_model.get_or_none(id=entity_id)
    fk_field = await get_filed_name(model)
    if not entity:
        return {"error": f"{owning_model} not found"}, 404

    notations = await model.filter(**{fk_field: entity_id}).all().prefetch_related("user")

    positive = sum(1 for n in notations if n.value == 1)
    negative = sum(1 for n in notations if n.value == -1)
    user_notation = next((n.value for n in notations if n.user.id == user.id), 0)

    return {
        "feedback_id": entity_id,
        "positive_notations": positive,
        "negative_notations": negative,
        "user_notation": user_notation,
    }, 200


