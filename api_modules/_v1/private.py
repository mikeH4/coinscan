from core.Address import Address
from typing import List, Optional
from time import time
from core.TokenRequest import TokenRequest
from core.Token import Token
from fastapi import APIRouter,HTTPException,Header
from pydantic import BaseModel
import settings

router = APIRouter(
    prefix="/private"
)

def check_api_key(auth):
    if settings.sandbox == True:
        return True
    if auth != "fneojNIOH*($H J)UJ)deU)#*I)(#@UHfew)*#":
        raise HTTPException(status_code=404, detail="Not Found")

@router.get("/")
def read_items():
    return {
        "actions": [route.path for route in router.routes]
    }

@router.get("/update/{address}")
def token(address: str, auth: Optional[str] = Header("")):
    check_api_key(auth)
    TokenRequest(address=address,request_time=time()).insert_or_ignore()
    return {"token": token}

@router.get("/update-queue")
def token(auth: Optional[str] = Header("")):
    check_api_key(auth)
    return {"token": TokenRequest.get_ordered()}

class ExternalToken(BaseModel):
    address: str
    name: str
    symbol: str
    decimals: int
    total_supply: int
    first_block: str
    block_time: Optional[int]


@router.post("/update-token")
def token(tokens:List[ExternalToken]):
    for token in tokens:
        address = Address(token.address)
        args = dict(
            address=address,
            name=token.name,
            symbol=token.symbol,
            total_supply=token.total_supply,
            decimals=token.decimals,
            block_time=0,
            first_seen=0,
            deployed=0,
            description="",
            bscscan_img="",
            holders=0,
            updated=time(),
            rating="",
            source_md5="",
        )
        for attr in ["block_time","first_seen","deployed","owner_renounced","dev_liquidity_check",
            "lp_check","top_holders_check","source_verified","honeypot_check",
            "similar_count","similar_viewable","no_older_tokens","not_proxy","not_pausable",
        ]:
            args[attr] = False

        dont_update = []
        ignore = True
        if getattr(token,"block_time"):
            dont_update = args.keys()
            ignore = False
            for arg in ["block_time","first_seen","deployed"]:
                dont_update.remove(arg)
                args[arg] = token.block_time

        Token(**args).insert_or_update(
            dont_update=dont_update,
            ignore=ignore
        )
        TokenRequest(
            address=address,
            request_time=time()
        )
