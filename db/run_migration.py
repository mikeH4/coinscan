from library.database.ModelOperator import ModelOperator
from library.database.postgres import DB
from db.models import models

with DB() as db:
    for cls in models:
        operator = ModelOperator(cls, db=db)
        operator.run_migration()