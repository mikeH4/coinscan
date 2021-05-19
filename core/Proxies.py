from requests.exceptions import ProxyError
from library.requests import get
from library.postgres import DB
from core.BaseModel import BaseModel
from random import choice
import json

class Proxies(BaseModel):
    table = "proxies"
    primary = ["ip"]

    def __init__(self, 
        ip:str,
        agent:str,
        status:str,
        added:int
    ) -> None: pass

    @classmethod
    def get_all(cls):
        with DB("tokens") as db:
            return [cls._from_row(row) for row in db.get_all("SELECT * FROM proxies")]

    @staticmethod
    def test(ip):
        try: get("https://google.com",proxy=ip)
        except ProxyError: return False
        return True

    @staticmethod
    def random_agent():
        with open("dataset/useragents.json","w+") as fp:
            return choice(json.load(fp))

    def remove(self, db: DB = None, replace = False):
        _db = DB("tokens") if db is None else db
        _db.query("DELETE FROM proxies WHERE ip = %s",[self.ip])
        if db is None:
            _db.close()
    
    def insert(self,db:DB = None,replace = False):
        _db = DB("tokens") if db is None else db
        _db.insert(
            self.table,
            self.dict(),
            replace_insert_on=["ip"] if replace else False,
            commit=False
        )
        if db is None:
            _db.close()