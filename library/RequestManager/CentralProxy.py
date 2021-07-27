from time import sleep, time
from urllib.parse import urlencode, urlparse, urlunparse
from requests.models import Response
from library.Proxies import Proxies
import requests

class CentralProxy:
    # keyed by class, each item containing available time
    _track = {}

    @classmethod
    def hold_fire(cls,_class):
        if cls._track[_class] <= time(): return

        sleep(cls._track[_class])
        
    
    @classmethod
    def with_trip(cls,_class, res: Response, kwargs: dict):
        if res.status_code == 429:
            available_in = int(res.headers["Retry-After"])
            cls._track[_class] = time()+available_in
            print(f"429: Sleeping for {available_in}")
            sleep(available_in)
            parsed_url = urlparse(res.request.headers["Forward-To"])._replace(query="")
            url = urlunparse(parsed_url)
            return cls.request(_class,url,**kwargs)
        return res

    @classmethod
    def init_slot(cls, _class):
        cls._track[_class] = time()

    @classmethod
    def request(cls, _class, url, **kwargs):
        cls.init_slot(_class)
        cls.hold_fire(_class)

        if "param_from_proxy" in kwargs:
            del kwargs["param_from_proxy"]
        res = forward_get(url,**kwargs)
        return cls.with_trip(_class, res, kwargs)
    
def forward_get(url,params={},headers={},cookies={},json={}):
    encoded_params = urlencode(params)
    encoded_params = ("" if encoded_params == "" else "?") + encoded_params
    
    full_url = url + encoded_params

    print(f"Request from rotating-proxy: {full_url}")
    headers["Forward-To"] = full_url

    res = requests.get(
        "http://147.182.192.210:8080",
        headers=headers,
        cookies=cookies,
        json=None if json == {} else json
    )
    return res