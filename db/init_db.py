import os

from tortoise import Tortoise

async def init_db():
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    # db_path = os.path.join("/mnt/data", "db.sqlite3")
    await Tortoise.init(
        db_url=f'sqlite://{db_path}',
        modules={'models': ['app.models']}
    )
    await Tortoise.generate_schemas(safe=True)  # creates missing tables only
    print(f"Database ready at {db_path}")

