from core.sources.CoinGecko import CoinGecko
from time import sleep, time
from datetime import datetime
from core.Address import Address
from core.Listing import Listing
from library.ratelimit import limits,sleep_and_retry
from core.sources.CoinMarketCap import CoinMarketCap

def update():
    # CoinMarketCap

    existing_cmc = Listing.get_by_platform("coinmarketcap")
    existing_slugs = [listing.local_slug for listing in existing_cmc]

    cmc = CoinMarketCap()
    listings = cmc.new()
    for listing in listings:
        if listing.get("platforms",False) and listing["platforms"][0]["id"] != 1839:
            continue
        if listing["slug"] in existing_slugs:
            continue
        token = cmc.single(slug=listing["slug"])
        
        platforms = token.get("platforms",[])
        if not platforms:
            continue
        address = None
        for platform in platforms:
            if platform["name"] == "Binance Smart Chain":
                address = platform["contractAddress"]
        if address is None:
            continue

        Listing(
            token=Address(address),
            local_id=token["id"],
            local_slug=token["slug"],
            platform="coinmarketcap",
            added=datetime.strptime(
                token["date_added"],
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ).timestamp(),
            updated=time()
        ).insert(replace=True)
        
    # CoinGecko

    cg = CoinGecko()
    listings = cg.listings()
    for listing in listings:
        token_address = listing["platforms"].get("binance-smart-chain",None) or ""
        token_address = str(Address(token_address.strip().lower()))
        if token_address == "":
            continue
        
        Listing(
            token=token_address,
            local_id=listing["id"],
            local_slug=listing["id"],
            platform="coingecko",
            added=time(),
            updated=time()
        ).insert(replace=True)

    print("Updated")

while True:
    next_in = 15*60
    update()
    sleep(next_in)
