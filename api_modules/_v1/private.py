from typing import Optional
from time import time
from core.TokenRequest import TokenRequest
from fastapi import APIRouter,HTTPException,Header
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