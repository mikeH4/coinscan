from fastapi import APIRouter

router = APIRouter(
    prefix="/latest"
)

@router.get("/all")
def all():
    return {"results": store}