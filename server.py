import uvicorn

ssl_cert = "/etc/letsencrypt/live/api.coinscan.finance/fullchain.pem"
ssl_key = "/etc/letsencrypt/live/api.coinscan.finance/privkey.pem"

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8888, log_level="info")