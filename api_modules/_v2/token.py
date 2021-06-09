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
def all(only_contract_verified: bool = False):
    return ViewableToken.get_latest(
        100,
        "WHERE source_verified = TRUE" if only_contract_verified else ""
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