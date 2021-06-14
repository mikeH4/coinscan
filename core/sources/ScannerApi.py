from library.BaseSource import BaseSource

class ScannerApi(BaseSource):
    url = "https://api2.coinscan.finance/"

    limit_calls = 1
    limit_period = 1

    def newly_added(self):
        res = self.request("/v1/private/new",headers=dict(
            auth="bON)Ihn(UB)B$#)TN$)UBOBNF)U$BNT)UB@$IJEHNU934NTU349B"
        ))
        return res.json()