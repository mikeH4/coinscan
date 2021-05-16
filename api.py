from fastapi import FastAPI

from api_modules import v1

app = FastAPI(openapi_url=None)

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
