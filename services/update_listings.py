def main():
    from library.Repeater import Repeater
    from core.sources.CoinGecko import CoinGecko
    from time import time
    from datetime import datetime
    from core.types.Address import Address
    from core.misc.Listing import Listing
    from core.sources.CoinMarketCap import CoinMarketCap, CoinMarketCapInternalApi


    repeater = Repeater(min=60*30,max=60*60)

    while True:
        with repeater.manager():
            print("Listing Loop Start")
            existing_cmc = Listing.get_by_platform("coinmarketcap")
            existing_slugs = [listing.local_slug for listing in existing_cmc]

            cmc = CoinMarketCap()
            cmc_api = CoinMarketCapInternalApi()
            listings = cmc.new()
            for listing in listings:
                if not listing.get("platforms",False) or listing["platforms"][0]["id"] != 1839:
                    continue
                if listing["slug"] in existing_slugs:
                    continue
                token = cmc_api.single(slug=listing["slug"])
                
                platforms = token.get("platforms",[])
                if not platforms:
                    continue
                address = None
                for platform in platforms:
                    if platform["contractPlatform"] == "Binance Smart Chain":
                        address = platform["contractAddress"]
                if address is None:
                    continue

                Listing(
                    token=Address(address),
                    local_id=token["id"],
                    local_slug=token["slug"],
                    platform="coinmarketcap",
                    added=datetime.strptime(
                        token["dateAdded"],
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).timestamp(),
                    updated=time()
                ).insert(replace=True)
                
            # CoinGecko

            cg = CoinGecko()
            listings = cg.listings()
            for listing in listings:
                token_address = listing["platforms"].get("binance-smart-chain",None) or ""
                try:
                    token_address = str(Address(token_address.strip().lower()))
                except TypeError:
                    continue
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

            print("Updated Listings")