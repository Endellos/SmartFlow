# test/conftest.py
import pytest
from tortoise import Tortoise
from tortoise.contrib.test import initializer, finalizer

async def init_inmemory_db():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={'models': ['app.models']}
    )
    await Tortoise.generate_schemas(safe=True)
    print("In-memory database ready")

async def close_inmemory_db():
    """Close all DB connections cleanly."""
    await Tortoise.close_connections()
    print("In-memory database closed")