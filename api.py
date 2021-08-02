from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import settings
from api_modules import v4

app = FastAPI(openapi_url=None)

if settings.sandbox == True:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

routers = [v4.app]

@app.get("/")
async def root():
    return {
        "actions": [router.prefix for router in routers]
    }

for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    ssl_cert = "/etc/letsencrypt/live/api.coinscan.finance/fullchain.pem"
    ssl_key = "/etc/letsencrypt/live/api.coinscan.finance/privkey.pem"

    if __name__ == "__main__":
        uvicorn.run("api:app", host="0.0.0.0", port=8888, log_level="info")