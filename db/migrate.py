from library.postgres import DB
from db.models import models

with DB() as db:
    for _class in models:
        new_cols = _class._db_new_cols()
        if len(new_cols) < 1:
            continue

        print(_class)
        print("New Columns:",new_cols)

        if input("Sure you want to overwrite?").lower() != "y":
            continue
        
        try:
            db.query(_class._db_recreate())
            db.conn.commit()
        except Exception as e:
            if input("Delete old temp table?").lower() == "y":
                db.rollback()
                db.query(f"DROP TABLE {_class.table}_temp;")
                db.query(_class._db_recreate())
                db.conn.commit()