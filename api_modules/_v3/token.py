from fastapi import APIRouter,HTTPException

from core.types.Address import Address

from core.Holders.ViewableHolders import ViewableHolders
from core.Token.ViewableToken import ViewableToken
from core.misc.ViewableListings import ViewableListings

router = APIRouter(
    prefix="/token"
)

@router.get("/{address}")
def token(address: str):
    try: address = Address(address)
    except: raise HTTPException(404)
    
    token = ViewableToken.get(address)
    if token is None: raise HTTPException(404)

    return token

@router.get("/{address}/wallets")
def wallets(address: str):
    try: address = Address(address)
    except: return []

    return ViewableHolders.top(address,limit=15)

@router.get("/{address}/listings")
def listings(address: str):
    try: address = Address(address)
    except: return []

    return {"listings": ViewableListings.get_listings(address)}