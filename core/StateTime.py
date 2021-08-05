from time import time
from typing import Optional
from library.database.postgres import DB
from core.types.db_types import bigint
from library.database.BaseModel import BaseModel

class StateTime(BaseModel):
    table = "state_time"
    
    primary = ["key","id","update"]

    def __init__(self,
        key: str,
        id: bigint,
        time: int,
        # Update or Add Time
        update: bool,
    ): pass

    @classmethod
    def upsert(cls,
        *,
        key: str,
        id: bigint,
        db: Optional[DB] = None
    ):
        query = f"""
        INSERT INTO state_time (key,id,time,update)
        VALUES ({DB.placeholder(3)}, FALSE)
        ON CONFLICT DO NOTHING;
        
        INSERT INTO state_time (key,id,time,update)
        VALUES ({DB.placeholder(3)}, TRUE)
        ON CONFLICT (key, id, update)
        DO UPDATE SET time = excluded.time
        ;
        """

        param = [key, id, int(time())]

        with cls.with_db(db) as db: db.query(query, param * 2)