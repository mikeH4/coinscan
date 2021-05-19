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
        raise HTTPException(status_code=404, detail="Not found")

    return {"token": token}

@router.get("/{address}")
def token(address: str):
    token = ViewableToken.get(address)
    if token is None:
        raise HTTPException(status_code=404, detail="Not found")

    return {"token": token}