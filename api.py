from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_modules import v1

app = FastAPI(openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

routers = [
    v1.app,
]

for router in routers:
    app.include_router(router)

@app.get("/")
async def root():
    return {
        "actions": [router.prefix for router in routers]
    }