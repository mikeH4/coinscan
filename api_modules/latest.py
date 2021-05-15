from fastapi import APIRouter
from core.ViewableToken import ViewableToken

router = APIRouter(
    prefix="/latest"
)

@router.get("/")
def read_items():
    return {
        "actions": [route.path for route in router.routes]
    }

@router.get("/get")
def all():
    return ViewableToken.get_latest(100)
