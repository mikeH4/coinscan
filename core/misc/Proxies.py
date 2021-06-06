from library.BaseSource import RequestPool
from requests.exceptions import ProxyError
from library.postgres import DB
from library.BaseModel import BaseModel
from random import choice
import json

class Proxies(BaseModel):
    table = "proxies"
    primary = ["ip","port"]

    def __init__(self, 
        ip:str,
        port:int,
        agent:str,
        added:int,
        # Meta
        bscscan_apikey:str,
        cmc_apikey:str
    ) -> None: pass

    @classmethod
    def get_all(cls):
        with DB("tokens") as db:
            return [cls._from_row(row) for row in db.get_all(
                f"SELECT * FROM proxies"
            )]

    @staticmethod
    def test_proxy(proxy):
        try:
            RequestPool._actual_request(
                "https://google.com",
                proxy=proxy
            )
        except ProxyError: return False
        return True

    def test(self):
        return self.test_proxy(self)

    @staticmethod
    def random_agent():
        with open("dataset/useragents.json","r") as fp:
            return choice(json.load(fp))
    
    def insert(self,db:DB = None,replace = False):
        with self.with_db(db) as db:
            db.insert(
                self.table,
                self.dict(),
                replace_insert_on=["ip"] if replace else False,
                commit=False
            )