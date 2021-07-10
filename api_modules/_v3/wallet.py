from core.Holders.ViewableAddressInfo import ViewableAddressInfo
from fastapi import APIRouter,HTTPException

from core.types.Address import Address

from core.Holders.ViewableHolders import ViewableHolders

router = APIRouter(
    prefix="/wallet"
)

@router.get("/{address}")
def token(address: str):
    try: address = Address(address)
    except: raise HTTPException(404)
    
    token = ViewableAddressInfo.get(address)
    if token is None: raise HTTPException(404)

    return token

@router.get("/{address}/tokens")
def token(address: str):
    try: address = Address(address)
    except: return []
    
    return ViewableHolders.get_tokens(address)