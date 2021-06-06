from core.misc.Proxies import Proxies
import json
from urllib.parse import urljoin
from time import time
import requests

class BaseSourceMetaClass(type):
    def __init__(cls, name, bases, namespace, **kwargs) -> None:
        if len(bases) < 1:
            return None
        if str(bases[0]) != "<class 'library.BaseSource.BaseSource'>":
            return None

        if cls.url is None:
            raise NotImplementedError("Class is invalid, url must be present")
        
# Abstract Clas
class BaseSource(metaclass=BaseSourceMetaClass):
    url = None
    limit_calls = 1
    limit_period = 1

    @staticmethod
    def parse_soup_json(soup,selector):
        script_content = soup.select(selector)[0].string
        return json.loads(script_content)

    def request(self,path,params={},headers={},cookies={}):
        return RequestPool.request(
            _class=self.__class__,
            url=urljoin(self.url,path),
            params=params,
            headers=headers,
            cookies=cookies
        )

    def get():
        raise NotImplementedError("get() must be defined in class")

class NoProxyInPool(Exception):
    def __init__(self, available_in:int) -> None:
        self.available_in = available_in
        super(NoProxyInPool, self).__init__("No proxy in pool")

class RequestPool:
    _proxies = []
    _track = {
        BaseSource: {
            Proxies(): [0,time()]
        }
    }

    @classmethod
    def _init_proxies(cls):
        proxies = Proxies.get_all()
        for proxy in proxies:
            if proxy.test():
                cls._proxies.append(proxy)
    
    @classmethod
    def _class_valid(cls):
        if not issubclass(cls,BaseSource):
            raise TypeError(f"{cls.__name__} does not inherit from BaseSource")

    @classmethod
    def _prepare_slot(cls,_class,proxy):
        if _class not in cls._track:
            cls._track[_class] = {}
        if proxy not in cls._track[_class]:
            cls._track[_class][proxy] = [0,time()]

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

        return (last_reset+_class.limit_period)-t

    @classmethod
    def _increment(cls,_class,proxy):
        cls._prepare_slot(_class,proxy)
        cls._track[_class][proxy] += 1


    @classmethod
    def request(cls,_class,url,**kwargs):
        cls._class_valid(_class)
        min_available_in = float("inf")
        for proxy in cls._proxies:
            available_in = cls._available_in(_class,proxy)
            min_available_in = min(min_available_in,available_in)
            if available_in > 0:
                continue
            cls._increment(_class,proxy)
            return cls._actual_request(url,proxy,**kwargs)
        raise NoProxyInPool(min_available_in)
    
    @classmethod
    def _actual_request(cls,url,proxy,params={},headers={},cookies={}):
        headers["User-Agent"] = proxy.agent

        req_proxy = None
        if proxy.ip != "":
            req_proxy = { 
                "http"  : f"http://{proxy.ip}:{proxy.port}", 
                "https" : f"http://{proxy.ip}:{proxy.port}",
            }
        
        return requests.get(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            proxy=req_proxy,
        )