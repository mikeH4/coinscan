from time import sleep, time
from urllib.parse import urlencode
from requests.models import Response
from library.Proxies import Proxies
import requests

class CentralProxy:
    # keyed by class, each item containing till value
    _track = {}

    _central_proxy = Proxies(
        ip="147.182.192.210",
        port="8080",
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
            available_in = 5
            print(f"429: Sleeping for {available_in}")
            return cls.request(_class,url=res.url,**kwargs)
        return res


    @classmethod
    def request(cls, _class, url, **kwargs):
        cls.hold_fire(_class)

        del kwargs["param_from_proxy"]
        res = forward_get(url,**kwargs)
        return cls.with_trip(_class,res,kwargs)
    
def forward_get(url,params={},headers={},cookies={},json={}):
    encoded_params = urlencode(params)
    encoded_params = ("" if encoded_params == "" else "?") + encoded_params
    
    full_url = url + encoded_params

    print(f"Request from rotating-proxy: {full_url}")
    headers["Forward-To"] = full_url

    res = requests.get(
        "http://147.182.192.210:8080",
        params=params,
        headers=headers,
        cookies=cookies,
        json=None if json == {} else json
    )
    return res