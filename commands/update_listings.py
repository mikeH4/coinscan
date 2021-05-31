from core.sources.CoinGecko import CoinGecko
from time import time
from datetime import datetime
from core.Address import Address
from core.Listing import Listing
from library.ratelimit import limits,sleep_and_retry
from core.sources.CoinMarketCap import CoinMarketCap

@sleep_and_retry
@limits(calls=2,period=60*20)
def update():
    # CoinMarketCap

    cmc = CoinMarketCap()
    listings = cmc.listings()
    for listing in listings:
        platform = listing.get("platform",None)
        if platform is None:
            continue
        if platform["name"] != "Binance Smart Chain":
            continue
        
        Listing(
            token=Address(platform["token_address"]),
            local_id=listing["id"],
            local_slug=listing["slug"],
            platform="coinmarketcap",
            added=datetime.strptime(
                listing["date_added"],
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ).timestamp(),
            updated=time()
        ).insert(replace=True)
        
    # CoinGecko

    cg = CoinGecko()
    listings = cg.listings()
    for listing in listings:
        token_address = listing["platforms"].get("binance-smart-chain",None) or ""
        token_address = token_address.strip().lower()
        if token_address == "":
            continue
        
        Listing(
            token=Address(token_address),
            local_id=listing["id"],
            local_slug=listing["id"],
            platform="coingecko",
            added=time(),
            updated=time()
        ).insert(replace=True)

    print("Updated")

while True:
    update()
