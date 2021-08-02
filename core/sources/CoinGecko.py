from typing import Optional
from core.StateTime import StateTime
from library.postgres import DB
from time import time
from core.Token.TokenListings import TokenListings
from core.types.AddressHash import AddressHash
from core.types.db_types import ChainEnum, PlatformsEnum, bigint
from library.RequestManager.CentralProxy import CentralProxy
from library.BaseSource import BaseSource

class CoinGecko(BaseSource):
    url = "https://api.coingecko.com"

    request_manager = CentralProxy

    def raw_listings(self):
        res = self.request(f"/api/v3/coins/list",params=dict(
            include_platform="true"
        ))
        try:
            return res.json()
        except ValueError:
            print("CoinGecko JSON error")
            return []
    
    def update_token_listings(self):
        chain_map: dict[str,ChainEnum] = {
            "binance-smart-chain": ChainEnum("bsc"),
            "ethereum": ChainEnum("eth")
        }

        with DB(auto_commit=True) as db:
            listings = self.raw_listings()
            for listing in listings:
                for chain_platform, token_address in listing["platforms"].items():
                    if chain_platform not in chain_map: continue
                    chain = chain_map[chain_platform]

                    token_address: str = token_address

                    try: token_address = AddressHash(token_address.strip())
                    except TypeError: continue

                    plt = "coingecko"
                    token_listing = TokenListings(
                        id=bigint(0),
                        platform=PlatformsEnum(plt),
                        local_id=listing["id"],
                        local_slug=listing["id"],
                        added=int(time())
                    )
                    id = token_listing.insert_or_update(
                        chain=chain,
                        token_address=token_address,
                        db=db
                    )
                    StateTime.upsert(
                        key=f"token_listing-{plt}",
                        id=id,
                        db=db
                    )