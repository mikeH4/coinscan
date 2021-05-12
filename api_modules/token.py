from fastapi import APIRouter,HTTPException
from api_modules.store import store

router = APIRouter(
    prefix="/token"
)

@router.get("/")
def read_items():
    return {
        "actions": [route.path for route in router.routes]
    }

@router.get("/search/{search}")
def token(search):
    search = search.lower()
    found = [token for token in store if (
        search == token["address"].lower() or 
        search in token["symbol"].lower() or 
        search in token["name"].lower()
    )]
    if not found:
        raise HTTPException(status_code=404, detail="Not found")

    return {"found": found}

@router.get("/{address}")
def token(address):
    found = [token for token in store if token["address"] == address]
    if not found:
        raise HTTPException(status_code=404, detail="Not found")

    return {"token": found[0]}