from fastapi import APIRouter,HTTPException
from api_modules._v1 import latest,token

app = APIRouter(
    prefix="/v1"
)

routers = [
    latest.router,
    token.router,
]

for router in routers:
    app.include_router(router)

@app.get("/")
async def root():
    return {
        "actions": [router.prefix for router in routers]
    }