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
        return self.request(
            f"/api",
            params=parameters
        ).json()

    def source_code(self,address:Address):
        while True:
            try:
                data = self.call("contract","getsourcecode",address=str(address))
                if data["status"] == "0":
                    raise BscScanApiException(data["result"])
                
                source = data["result"][0]["SourceCode"]
                return None if source == "" else source
            except BscScanApiException:
                sleep(3)