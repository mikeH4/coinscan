from core.StateTime import StateTime
from library.postgres import DB
from core.Token.TokenListings import TokenListings
from datetime import datetime
from core.types.AddressHash import AddressHash
from core.types.db_types import ChainEnum, PlatformsEnum, bigint
from library.RequestManager.CentralProxy import CentralProxy
from library.BaseSource import BaseSource
from bs4 import BeautifulSoup

class CoinMarketCap(BaseSource):
    url = "https://coinmarketcap.com/"

    request_manager = CentralProxy

    def new(self):
        res = self.request(f"/new/")
        soup = BeautifulSoup(res.text,"html.parser")
        data = self.parse_soup_json(soup,"#__NEXT_DATA__")
        raw = data["props"]["initialState"]["cryptocurrency"]["new"]["data"]
        return raw

    @staticmethod
    def _is_listing_valid(listing: dict):
        # Validation
        if not listing.get("platforms", False):
            print(f"No Platform for token {listing['slug']}")
            return False
        
        platform_valid = False
        for chain_platform in listing["platforms"]:
            if chain_platform["id"] in [1027,1839]: platform_valid = True
        
        if not platform_valid:
            print(f"No existing platform for {listing['slug']}")
            return False
        
        return True

    def update_token_listings(self):
        listings = self.new()
        with DB(auto_commit=True) as db:
            for listing in listings:
                # Validation
                if not self._is_listing_valid(listing): continue

                token = CoinMarketCapInternalApi().single(slug=listing["slug"])
                
                platforms = token.get("platforms",[])
                # [] counts as not
                if not platforms:
                    print("No platform field or empty platforms")
                    continue

                # Actual Processing

                chain_map: dict[str, ChainEnum] = {
                    "Binance Smart Chain": ChainEnum("bsc"),
                    "Ethereum": ChainEnum("eth")
                }

                for chain_platform in platforms:
                    chain_platform_name = chain_platform["contractPlatform"]
                    if chain_platform_name not in chain_map:
                        print(f"Unsupported Contract Platform: {chain_platform_name}")
                        continue
                    chain = chain_map[chain_platform_name]

                    address = chain_platform["contractAddress"]
                    if address is None:
                        print("Address is none")
                        continue
                    address = AddressHash(address)

                    added = datetime.strptime(
                        token["dateAdded"],
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).timestamp()

                    print(f"Added {token['slug']}: {address} with {token['dateAdded']}")

                    plt = "coinmarketcap"
                    id = TokenListings(
                        id=bigint(0),
                        platform=PlatformsEnum(plt),
                        local_id=token["id"],
                        local_slug=token["slug"],
                        added=int(added)
                    ).insert_or_update(
                        chain=chain,
                        token_address=address,
                        db=db
                    )
                    StateTime.upsert(
                        key=f"token_listing-{plt}",
                        id=id,
                        db=db
                    )
                    

class CoinMarketCapInternalApi(BaseSource):
    url = "https://api.coinmarketcap.com"

    request_manager = CentralProxy

    limit_calls = 1
    limit_period = 5

    def single(self, *, slug):
        res = self.request(
            f"/data-api/v3/cryptocurrency/detail",
            params=dict(
                slug=slug,
                langCode="en",
                aux="status",
            )
        )
        return res.json()["data"]


class CoinMarketCapProApi(BaseSource):
    url = "https://pro-api.coinmarketcap.com/"

    request_manager = CentralProxy

    def all(self):
        ls = []
        page = 0
        while page * 5000 == len(ls):
            res = self.request(
                f"/v1/cryptocurrency/listings/latest",
                params=dict(
                    limit=5000,
                    start=(page*5000)+1
                )
            )
            ls += res.json()["data"]
            page += 1
        return ls