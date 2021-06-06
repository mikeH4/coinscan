from core.types.Address import Address
from library.BaseSource import BaseSource

class BscScanApi(BaseSource):
    url = "https://api.bscscan.com/"

    limit_calls = 4
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
        data = self.call("contract","getsourcecode",address=str(address))
        if data["status"] == "0":
            raise Exception(data["result"])
        
        source = data["result"][0]["SourceCode"]
        return None if source == "" else source