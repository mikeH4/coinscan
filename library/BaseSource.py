from library.request import get
from library.Proxies import Proxies
import json
from urllib.parse import urljoin
from time import time

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
    require_in_proxy=[]

    @staticmethod
    def parse_soup_json(soup,selector):
        script_content = soup.select(selector)[0].string
        return json.loads(script_content)

    def request(self,path,params={},headers={},cookies={}):
        return RequestPool.request(
            _class=self.__class__,
            url=urljoin(self.url,path),
            require_in_proxy=self.__class__.require_in_proxy,
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
    _track = {}

    @classmethod
    def _init_proxies(cls):
        proxies = Proxies.get_all()
        for proxy in proxies:
            if proxy.test():
                cls._proxies.append(proxy)
    
    @staticmethod
    def _class_valid(_class):
        if not issubclass(_class,BaseSource):
            raise TypeError(f"{_class.__name__} does not inherit from BaseSource")

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
        if num < _class.limit_calls:
            return 0

        return (last_reset+_class.limit_period)-t

    @classmethod
    def _increment(cls,_class,proxy):
        cls._prepare_slot(_class,proxy)
        cls._track[_class][proxy][0] += 1

    @classmethod
    def request(cls,_class,url,require_in_proxy=[],**kwargs):
        cls._class_valid(_class)
        min_available_in = float("inf")
        for proxy in cls._proxies:
            if not proxy.has(require_in_proxy):
                print("Does not have:",require_in_proxy)
                continue
            
            available_in = cls._available_in(_class,proxy)
            min_available_in = min(min_available_in,available_in)
            if available_in > 0:
                continue
            cls._increment(_class,proxy)
            return get(url,proxy,**kwargs)
        
        raise NoProxyInPool(min_available_in)

RequestPool._init_proxies()