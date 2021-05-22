from time import time
from core.TokenRequest import TokenRequest
from core.ViewableHolders import ViewableHolders
from core.Holders import Holders
from fastapi import APIRouter,HTTPException
from core.ViewableToken import ViewableToken

router = APIRouter(
    prefix="/token"
)

@router.get("/")
def read_items():
    return {
        "actions": [route.path for route in router.routes]
    }

@router.get("/search/{search}")
def token(search: str):
    tokens = ViewableToken.search(search)
    return tokens

@router.get("/{address}")
def token(address: str):
    token = ViewableToken.get(address)
    if token is None:
        TokenRequest(address=address,request_time=time()).insert_or_ignore()
        raise HTTPException(status_code=404, detail="Not found")

    return {"token": token}

@router.get("/{address}/holders")
def token(address: str):
    return {"holders": ViewableHolders.filter_top_holders(ViewableHolders.top(address))}