from fastapi import APIRouter
from api_modules._v4 import token, private, wallet, feed

app = APIRouter(
    prefix="/v4"
)

routers = [
    token.router,
    private.router,
    wallet.router,
    feed.router
]

for router in routers:
    @router.get("/")
    def index(): return dict(action=[route.path for route in router.routes])
    
    app.include_router(router)

@app.get("/")
def root_index(): return dict(actions=[router.prefix for router in routers])