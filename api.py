from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_modules import v1

app = FastAPI(openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["coinscan.finance"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["DNT","X-Mx-ReqToken","Keep-Alive","User-Agent","X-Requested-With","If-Modified-Since","Cache-Control","Content-Type","X-Api-Auth"],
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
