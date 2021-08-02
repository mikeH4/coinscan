from core.types.AddressHash import AddressHash
from urllib.parse import urljoin
from core.types.db_types import ChainEnum, numeric
from library.BaseSource import BaseSource
from library.RequestManager.NoProxy import NoProxy

class ScannerApi(BaseSource):
    url = "https://api2.coinscan.finance/"

    request_manager = NoProxy

    auth_headers = {
        "auth": "bON)Ihn(UB)B$#)TN$)UBOBNF)U$BNT)UB@$IJEHNU934NTU349B",
        "X-Api-Auth": "5ad6c116cda6f75000ee2c943d406516a6332718e90c87833ffecfef2f58f34e"
    }

    def req(self, chain: ChainEnum, path: str, *args, **kwargs):
        path = path.lstrip("/")
        chain = ChainEnum(chain)
        return self.request(urljoin(f"/v1/{chain}/",path),*args,**kwargs)

    def new(self, chain: ChainEnum):
        res = self.req(chain,"/v1/private/new",headers=self.auth_headers)
        return res.json()
    
    def get_addresses(self, chain: ChainEnum, * , addresses: list[AddressHash]):
        res = self.req(chain,f"/v1/private/get",headers=self.auth_headers,json=dict(
            addresses=addresses
        ))
        return res.json()
    
    def prices(self, chain: ChainEnum) -> list[tuple[str, numeric, numeric, numeric]]:
        res = self.req(chain,"/v1/private/liquidity",headers=self.auth_headers)
        return res.json()

    def busd(self, chain: ChainEnum):
        res = self.req(chain,f"/v1/private/busd",headers=self.auth_headers)
        return res.json()

    def token_pairs_count(self, chain: ChainEnum):
        res = self.req(chain,f"/v1/private/token-pairs-count",headers=self.auth_headers)
        return res.json()["count"]

    def token_pairs(self,
        chain: ChainEnum,
        *,
        limit: int = 100,
        offset: int = 0
    ):
        res = self.req(chain,f"/v1/private/token-pairs?limit={limit}&offset={offset}",headers=self.auth_headers)
        return res.json()