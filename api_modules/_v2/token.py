from time import time

from core.misc.TokenRequest import TokenRequest
from core.Holders.ViewableHolders import ViewableHolders
from core.Holders.Holders import Holders
from fastapi import APIRouter,HTTPException
from core.Token.ViewableToken import ViewableToken

router = APIRouter(
    prefix="/token"
)

@router.get("/latest")
def all(only_contract_verified: bool = False,min_liquidity_500 = False):
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