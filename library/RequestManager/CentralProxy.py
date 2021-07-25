from time import sleep, time
from library.request import get
from requests.models import Response
from library.Proxies import Proxies

class CentralProxy:
    # keyed by class, each item containing till value
    _track = {}

    _central_proxy = Proxies(
        ip="147.182.139.229",
        port="5566",
        agent="",
        added=time(),
        bscscan_apikey="",
        cmc_apikey=""
    )

    @classmethod
    def hold_fire(cls,_class):
        if _class not in cls._track: return
        if cls._track[_class] <= time(): return

        sleep(cls._track[_class])
        
    
    @classmethod
    def with_trip(cls,_class, res: Response, kwargs: dict):
        if res.status_code == 429:
            available_in = int(res.headers["available-in"])
            cls._track[_class] = time()+available_in
            sleep(available_in)
            return cls.request(_class,url=res.url,**kwargs)
        return res


    @classmethod
    def request(cls, _class, url, **kwargs):
        cls.hold_fire(_class)

        res = get(url,cls._central_proxy,**kwargs)
        return cls.with_trip(_class,res,kwargs)
