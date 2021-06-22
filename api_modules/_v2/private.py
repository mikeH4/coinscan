from library.postgres import DB
from api_modules._v2.token import listings
from core.Token.ViewableToken import ViewableToken
from core.types.Address import Address
import settings
from fastapi import APIRouter,HTTPException,Header

from typing import List,Optional
from pydantic import BaseModel

router = APIRouter(
    prefix="/private"
)

def check_api_key(auth):
    if settings.sandbox == True:
        return True
    if auth != "j23j90rhn)#@p23j09h)*IH#@)(H#@IRJT)I@#HT(FH@#N)TJ_(@IHNof j4900tjf0t34":
        raise HTTPException(status_code=404, detail="Not Found")

class ItemsSections(BaseModel):
    listings: List[List[str]]
    addresses: List[str]

@router.post("/from-items")
async def new_tokens(
    items: ItemsSections,
    auth: Optional[str] = Header("")
) -> list:
    check_api_key(auth)
    conds = []
    params = []
    for platform,name in items.listings:
        params.append(platform)
        params.append(name)
        conds.append(f"(platform = {DB.placeholder(1)} AND local_slug = {DB.placeholder(1)})")

    params += items.addresses
    if len(items.addresses) > 0:
        conds.append(f"tokens.address IN ({DB.placeholder(len(items.addresses))})")

    if len(conds) < 1:
        return []

    sql = ViewableToken._build_query(f"""
    LEFT JOIN
        listings as listings_full
    ON listings_full.token = tokens.address
    WHERE
        ({' OR '.join(conds)})
    """)
    with DB("tokens") as db:
        addresses = {}
        tokens = []
        for row in db.get_all(sql,params):
            address = str(Address(row[0]))
            if address in addresses:
                continue
            addresses[address] = True
            tokens.append(ViewableToken._from_row(row))
        return tokens