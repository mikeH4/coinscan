from core.CoreToken import CoreToken
from library.sqlite import DB

class Token(CoreToken):
    @staticmethod
    def _get_latest_in_rows(limit=100):
        limit_cond = ""
        if limit is not None:
            limit_cond = f"LIMIT {int(limit)}"

        with DB("tokens") as db:
            return db.get_all(f"SELECT * FROM tokens ORDER BY block_time DESC {limit_cond}")

    @classmethod
    def _from_row(cls,row):
        token = cls({key:row[i] for i,key in enumerate(cls.keys)})
        return token

    @classmethod
    def get_latest(cls,limit=100):
        rows = cls._get_latest_in_rows(limit=limit)
        return [cls._from_row(row) for row in rows]

    @classmethod
    def search(cls,keyword,limit=10):
        limit_cond = ""
        if limit is not None:
            limit_cond = f"LIMIT {int(limit)}"
        with DB("tokens") as db:
            placeholder = db.placeholder(1)
            sql = f"""
            SELECT * FROM tokens
            WHERE
            address = {placeholder}
            OR symbol LIKE {placeholder}
            OR name LIKE {placeholder}
            {limit_cond}
            """
            rows = db.get_all(sql,[keyword,*["%" + keyword + "%"] * 2])
            return [cls._from_row(row) for row in rows]

    @classmethod
    def get(cls, address):
        with DB("tokens") as db:
            placeholder = db.placeholder(1)
            token = db.get(f"SELECT * FROM tokens WHERE address = {placeholder}",[address])
            if token is None:
                return None
            return cls._from_row(token)
        
    def insert_or_update(self,db:DB = None):
        _db = db if db is not None else DB("tokens")

        _dict = self.dict()
        address = _dict["address"]
        _dict["address"] = str(_dict["address"])
        _db.insert(
            "tokens",
            _dict,
            replace_insert="address",
            commit=False
        )
        print("Inserted:", address)

        if db is None:
            _db.close()