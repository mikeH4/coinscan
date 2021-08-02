from library.postgres import DB
from db.models import models

with DB() as db:
    rows = db.get_all("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """)
    tables = [row[0] for row in rows]

    for _class in models:
        if _class.table in tables:
            continue

        print(_class)
        if input(f"Create table '{_class.table}'?").lower() != "y":
            continue

        db.query(_class._db_create())
        db.conn.commit()
