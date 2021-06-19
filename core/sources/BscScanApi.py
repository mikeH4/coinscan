from time import sleep
from core.types.Address import Address
from library.BaseSource import BaseSource

class BscScanApiException(Exception):
    pass

class BscScanApi(BaseSource):
    url = "https://api.bscscan.com/"

    limit_calls = 3
    limit_period = 1

    param_from_proxy = dict(
        bscscan_apikey="apikey"
    )

    def call(self,module,action,**parameters):
        parameters.update(
            module=module,
            action=action
        )
        data = self.request(
            f"/api",
            params=parameters
        ).json()
        if data["status"] == "0":
            raise BscScanApiException(data["result"])
        return data

    def source_code(self,address:Address):
        while True:
            try:
                data = self.call("contract","getsourcecode",
                    address=str(address)
                )                
                source = data["result"][0]["SourceCode"]
                return None if source == "" else source
            except BscScanApiException:
                sleep(3)
    
    def total_supply(self,address:Address):
        data = self.call("stats","tokensupply",
            contractaddress=str(address)
        )
        return float(data["result"])
