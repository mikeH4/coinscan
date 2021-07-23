from library.BaseModel import BaseModel
from library.postgres import DB
from core.types.Address import Address
from core.types.db_types import bigint, numeric
import csv
import os

class TokenPrices(BaseModel):
    table = "token_prices"
    primary = ["token"]

    def __init__(self,
        token: Address,
        price_change: bigint,
        circulating: numeric,
        liquidity: numeric
    ) -> None: pass
    
    @classmethod
    def completely_absolutely_replace(cls,data:list):
        with open("temp.csv", "w+", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        with DB(auto_commit=False) as db:
            db.query("DELETE FROM token_prices")
            with open("temp.csv","r") as f:
                db.cursor.copy_from(f, "token_prices", columns=("token","price_change","circulating","liquidity"), sep=",")
            db.conn.commit()
        os.remove("temp.csv")

    @classmethod
    def rising(cls, db:DB = None):
        with cls.with_db(db) as db:
            rows = db.get_all("""
            SELECT
                token,
                price_change
            FROM token_prices
            WHERE liquidity >= 2
            ORDER BY price_change DESC
            LIMIT 100
            """)
            rising_dict = {}
            for token,price_change in rows:
                rising_dict[token] = price_change
            return rising_dict

