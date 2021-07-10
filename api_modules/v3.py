from fastapi import APIRouter
from api_modules._v3 import token
from api_modules._v3 import feed
from api_modules._v3 import private
from api_modules._v3 import wallet

app = APIRouter(
    prefix="/v3"
)

routers = [
    token.router,
    private.router,
    feed.router,
    wallet.router
]

for router in routers:
    @router.get("/")
    def index(): return dict(action=[route.path for route in router.routes])
    
    app.include_router(router)

@app.get("/")
def root_index(): return dict(actions=[router.prefix for router in routers])
