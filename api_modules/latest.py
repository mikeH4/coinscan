from fastapi import APIRouter
from api_modules.store import store

router = APIRouter(
    prefix="/latest"
)

@router.get("/")
def read_items():
    return {
        "actions": [route.path for route in router.routes]
    }


@router.get("/all")
def all():
    return {"results": store}