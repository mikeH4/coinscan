from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_modules import latest
from api_modules import token

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

routers = [
    latest.router,
    token.router,
]

for router in routers:
    router.get("/")(lambda: {
        "actions": [route.path for route in router.routes]
    })
    app.include_router(router)

@app.get("/")
async def root():
    return {
        "actions": [router.prefix for router in routers]
    }