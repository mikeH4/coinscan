from fastapi import APIRouter
from api_modules._v3 import token
from api_modules._v3 import feed
from api_modules._v3 import private

app = APIRouter(
    prefix="/v3"
)

routers = [
    token.router,
    private.router,
    feed.router,
]

for router in routers:
    @router.get("/")
    def index():
        return {
            "actions": [route.path for route in router.routes]
        }
    app.include_router(router)

@app.get("/")
async def root_index():
    return {
        "actions": [router.prefix for router in routers]
    }