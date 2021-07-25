from library.request import get
from time import sleep, time
from library.Proxies import Proxies

class NoProxyInPool(Exception):
    def __init__(self, available_in:int) -> None:
        self.available_in = available_in
        super(NoProxyInPool, self).__init__("No proxy in pool")


class RequestPool:
    _proxies = []
    _track = {}
    _total = {}

    @classmethod
    def _init_proxies(cls):
        proxies = Proxies.get_all()
        for proxy in proxies:
            if proxy.test():
                cls._proxies.append(proxy)
    
    @classmethod
    def _prepare_slot(cls,_class,proxy):
        for _dict in [cls._track,cls._total]:
            if _class not in _dict:
                _dict[_class] = {}
            if proxy not in _dict[_class]:
                _dict[_class][proxy] = [0,time()]

    @classmethod
    def _available_in(cls,_class,proxy):
        cls._prepare_slot(_class,proxy)
        num,last_reset = cls._track[_class][proxy]
        t = time()
        # Reset if exceeded period
        # time since last reset > limit_period
        if (t - last_reset) > _class.limit_period:
            cls._track[_class][proxy] = [0,t]

        num,last_reset = cls._track[_class][proxy]
        if _class.__name__ == "BscScanApi":
            print(f"{_class.__name__}: {num} => {time()-last_reset} [{proxy.ip}] # [{proxy.bscscan_apikey}]")
        if num < _class.limit_calls:
            return 0

        return (last_reset+_class.limit_period)-t

    @classmethod
    def _increment(cls,_class,proxy):
        cls._prepare_slot(_class,proxy)
        cls._track[_class][proxy][0] += 1
        cls._total[_class][proxy][0] += 1

    @classmethod
    def request_internal(cls,_class,url,param_from_proxy={},**kwargs):
        min_available_in = float("inf")
        for proxy in cls._proxies:
            params = proxy.update_params(
                param_from_proxy,
                kwargs["params"]
            )
            if params is None:
                print("No Params")
                print(proxy.bscscan_apikey)
                continue
            kwargs["params"] = params
            
            available_in = cls._available_in(_class,proxy)
            min_available_in = min(min_available_in,available_in)
            if available_in > 0:
                if _class.__name__ == "BscScanApi":
                    print("Available In:",available_in)
                continue
            
            cls._increment(_class,proxy)
            return get(url,proxy,**kwargs)
        
        raise NoProxyInPool(min_available_in)

    @classmethod
    def request(cls,_class,url,**kwargs):
        while True:
            try:
                return cls.request_internal(_class,url,**kwargs)
            except NoProxyInPool as e:
                print(f"Limit exhausted: Sleeping for {e.available_in}")
                sleep(e.available_in)