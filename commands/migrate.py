from core.CoreToken import CoreToken
from core.Holders import Holders
from library.postgres import DB

db = DB("tokens")

for _class in [CoreToken,Holders]:
    print(_class)
    print("New Columns:",_class._db_new_cols())

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