from library.request import get
from time import time
from library.Proxies import Proxies

class TorRequestExceed(Exception):
    def __init__(self, available_in:int) -> None:
        self.available_in = available_in
        super(TorRequestPool, self).__init__("Tor requests exceeded")

class TorRequestPool:
    _track = [0,time()]

    _tor_proxy = Proxies(
        ip="147.182.139.229",
        port="5566",
        agent=Proxies.random_agent(),
        added=time(),
        bscscan_apikey="",
        cmc_apikey=""
    )
    _tor_limit_calls = 25
    _tor_limit_period = 1

    @classmethod
    def _increment(cls):
        cls._track[0] += 1

    @classmethod
    def _available_in(cls):
        num,last_reset = cls._track
        t = time()
        # Reset if exceeded period
        # time since last reset > limit_period
        if (t - last_reset) > cls._tor_limit_period:
            cls._track = [0,t]

        num,last_reset = cls._track
        if num < cls._tor_limit_calls:
            return 0

        return (last_reset+cls._tor_limit_period)-t

    @classmethod
    def request(cls,_class,url,param_from_proxy={},**kwargs):
        available_in = cls._available_in()
        if available_in > 0:
            raise TorRequestExceed(available_in)
        
        cls._increment()

        cls._tor_proxy.agent = Proxies.random_agent()

        return get(url,cls._tor_proxy,**kwargs)

