from core.types.Address import Address
from core.sources.BaseSource import BaseSource

class BscScanApi(BaseSource):
    url = "https://api.bscscan.com/"

    limit_calls = 4
    limit_period = 1

    def __init__(self, apikey, **kwds) -> None:
        for attr in ["proxy","agent"]:
            setattr(self,attr,kwds.get(attr,None))
        self.apikey = apikey

    def call(self,module,action,**parameters):
        params = [
            f"{key}={value}"
            for key,value
            in parameters.items()
        ]
        param_string = "" if len(params) < 1 else "&" + ('&'.join(params))
        query_string = f"?module={module}&action={action}&apikey={self.apikey}{param_string}"
        return self.request(f"/api{query_string}").json()

    def source_code(self,address:Address):
        data = self.call("contract","getsourcecode",address=str(address))
        if data["status"] == "0":
            raise Exception(data["result"])
        
        source = data["result"][0]["SourceCode"]
        return None if source == "" else source