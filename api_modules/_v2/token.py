from time import time
from fastapi import APIRouter,HTTPException

from library.postgres import DB

from core.misc.TokenRequest import TokenRequest

from core.Holders.ViewableHolders import ViewableHolders
from core.Holders.Holders import Holders
from core.Token.ViewableToken import ViewableToken
from core.misc.Listing import Listing

router = APIRouter(
    prefix="/token"
)

@router.get("/latest")
def latest(only_contract_verified:bool=False, min_liquidity_500:bool=False):
    with_liquidity = False
    where = []
    if only_contract_verified:
        where.append("source_verified = TRUE")
    if min_liquidity_500:
        with_liquidity = True
        where.append("liquidity.liquidity > 500")

    return ViewableToken.get_latest(
        limit=100,
        where_cond="" if len(where) < 1 else "WHERE " + (" AND ".join(where)),
        with_liquidity=with_liquidity
    )

@router.get("/listings")
def listings():
    with DB("tokens") as db:
        listings = Listing.new_listings(db=db)
        listing_keys = list(listings.keys())
        tokens = ViewableToken.get_addresses(
            listing_keys,
            db=db
        )
        sorted_tokens = []
        for address in listing_keys:
            if address not in tokens:
                del listings[address]
                continue
            sorted_tokens.append(tokens[address])
        return dict(
            listings=listings,
            tokens=sorted_tokens
        )

@router.get("/search/{search}")
def search(search: str):
    tokens = ViewableToken.search(search)
    return tokens

@router.get("/get/{address}")
def token(address: str):
    token = ViewableToken.get(address)
    if token is None:
        TokenRequest(address=address,request_time=time()).insert_or_ignore()
        raise HTTPException(status_code=404, detail="Not found")

    return {"token": token}

@router.get("/get/{address}/holders")
def holders(address: str):
    return {"holders": ViewableHolders.top(address)}