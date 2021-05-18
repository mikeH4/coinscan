from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_modules import v1
import settings

app = FastAPI(openapi_url=None)

if settings.sandbox == True:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


routers = [
    v1.app,
]

@app.get("/")
async def root():
    return {
        "actions": [router.prefix for router in routers]
    }

for router in routers:
    app.include_router(router)
