from library.BaseModel import BaseModel
from library.postgres import DB
from core.types.Address import Address
from core.types.db_types import numeric
import csv
import os

class TokenPrices(BaseModel):
    table = "token_prices"
    primary = ["token"]

    def __init__(self,
        token: Address,
        price_change: int,
        circulating: numeric,
        liquidity: numeric
    ) -> None: pass
    
    @classmethod
    def completely_absolutely_replace(cls,data:list):
        with open("temp.csv", "w+", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        with DB("tokens",auto_commit=False) as db:
            db.query("DELETE FROM token_prices")
            with open("temp.csv","r") as f:
                db.cursor.copy_from(f, "token_prices", columns=("token","price_change","circulating","liquidity"), sep=",")
        os.remove("temp.csv")