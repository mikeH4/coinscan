from core.types.db_types import ChainEnum
from library.RequestManager.CentralProxy import CentralProxy
from time import sleep
from core.types.AddressHash import AddressHash
from library.BaseSource import BaseSource

class BscScanApiException(Exception):
    pass

class BscScanApi(BaseSource):
    url = "https://api.bscscan.com/"

    request_manager = CentralProxy

    def call(self,module,action,**parameters):
        parameters.update(
            module=module,
            action=action
        )
        res = self.request(
            f"/api",
            params=parameters
        )
        data = res.json()
        if data["status"] == "0":
            raise BscScanApiException(data["result"])
        return data

    def source_code(self, address: AddressHash):
        while True:
            try:
                data = self.call("contract","getsourcecode",
                    address=str(address)
                )
                source = data["result"][0]["SourceCode"]
                return None if source == "" else source
            except BscScanApiException:
                sleep(3)
    
    def total_supply(self,address: AddressHash):
        data = self.call("stats","tokensupply",
            contractaddress=str(address)
        )
        return float(data["result"])

class EtherScanApi(BscScanApi):
    url = "https://api.etherscan.io"


class ChainScanApi():
    def __new__(cls, chain: ChainEnum):
        if chain == "bsc":
            return BscScanApi()
        elif chain == "eth":
            return EtherScanApi()
        raise TypeError(f"{chain} is not a valid chain")