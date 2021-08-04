from time import sleep, time
from urllib.parse import urlencode, urlparse, urlunparse
from requests.models import Response
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

        res = forward_get(url,**kwargs)
        return cls.with_trip(_class, res, kwargs)
    
def forward_get(url,params={},headers={},json={}):
    encoded_params = urlencode(params)
    encoded_params = ("" if encoded_params == "" else "?") + encoded_params
    
    full_url = url + encoded_params

    print(f"Request from rotating-proxy: {full_url}")
    headers["Forward-To"] = full_url

    res = requests.get(
        "https://connect.flek.cloud",
        headers=headers,
        json=None if json == {} else json
    )
    return res