from library.BaseSource import BaseSource

class ScannerApi(BaseSource):
    url = "https://api2.coinscan.finance/"

    limit_calls = 1
    limit_period = 1

    # Only use in exceptional cases
    auth_headers = {
        "auth": "bON)Ihn(UB)B$#)TN$)UBOBNF)U$BNT)UB@$IJEHNU934NTU349B",
        "X-Api-Auth": "5ad6c116cda6f75000ee2c943d406516a6332718e90c87833ffecfef2f58f34e"
    }

    def __init__(self,limit_bypass=False) -> None:
        self.limit_bypass = limit_bypass

    def new(self):
        res = self.request("/v1/private/new",headers=self.auth_headers)
        return res.json()
    
    def get_addresses(self,addresses):
        res = self.request(f"/v1/private/get",headers=self.auth_headers,json=dict(
            addresses=list(map(str,addresses))
        ))
        return res.json()
    
    def prices(self):
        res = self.request("/v1/private/liquidity",headers=self.auth_headers)
        return res.json()

    def busd(self):
        res = self.request(f"/v1/private/busd",headers=self.auth_headers)
        return res.json()

    def token_pairs_count(self):
        res = self.request(f"/v1/private/token-pairs-count",headers=self.auth_headers)
        return res.json()["count"]

    def token_pairs(self, limit=100, offset=0):
        res = self.request(f"/v1/private/token-pairs?limit={limit}&offset={offset}",headers=self.auth_headers)
        return res.json()