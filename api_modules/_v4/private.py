from library.database.postgres import DB
from core.Token.ViewableToken import ViewableToken
from core.types.AddressHash import AddressHash
import settings
from fastapi import APIRouter, HTTPException, Header

from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(
    prefix="/private"
)

def authenticate(auth):
    if settings.sandbox == True: return True
    if auth != "j23j90rhn)#@p23j09h)*IH#@)(H#@IRJT)I@#HT(FH@#N)TJ_(@IHNof j4900tjf0t34":
        raise HTTPException(404)
    return True

class ItemsSections(BaseModel):
    listings: List[List[str]]
    addresses: List[AddressHash]

@router.post("/from-items")
def new_tokens(
    items: ItemsSections,
    auth: Optional[str] = Header("")
) -> list:
    authenticate(auth)
    conds = []
    params = []
    for platform,name in items.listings:
        params.append(platform)
        params.append(name)
        conds.append(f"(token_listings.platform = {DB.placeholder(1)} AND token_listings.local_slug = {DB.placeholder(1)})")

    items.addresses = [AddressHash(address) for address in items.addresses]
    params += items.addresses
    if len(items.addresses) > 0:
        conds.append(f"address.address IN ({DB.placeholder(len(items.addresses))})")

    if len(conds) < 1:
        return []

    cond_str = f"WHERE ({' OR '.join(conds)})"
    sql = f"""
    SELECT
        address.chain AS chain,
        address.address AS address
    FROM address
    JOIN address ON token_meta.id = address.id
    LEFT JOIN token_listings ON token_listings.id = address.id
    {cond_str}
    """
    with DB() as db:
        tokens = [
            dict(
                chain=chain,
                address=AddressHash(address)
            )
            for chain, address
            in set(db.get_all(sql,params))
        ]
        return tokens