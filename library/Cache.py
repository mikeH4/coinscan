from time import time

class CacheItem():
    def __init__(self, data, cache_for:int=True) -> None:
        self._expiry = None if cache_for == True else time()+int(cache_for)
        self._data = data
    def get(self):
        return self._data
    def expired(self):
        expired = self._expiry is not None and time() >= self._expiry
        if expired: print("Cache Expired")
        return expired

class Cache:
    _store = {}

    @classmethod
    def _slot (cls, type:str) -> dict:
        if type not in cls._store:
            cls._store[type] = {}
        return cls._store[type]

    @classmethod
    def get (cls, type, key):
        slot = cls._slot(type)
        cache_item_or_None = slot.get(key,None)
        if cache_item_or_None is None or cache_item_or_None.expired():
            return None
        return cache_item_or_None

    @classmethod
    def put (cls,type,key,item:CacheItem):
        cls._slot(type)[key] = item
    
    # Helper
    @staticmethod
    def wrap(cache_args:tuple[str], cache_for=True):
        """
        cache_for may by True | int | lambda : int
        """
        def decorator(func):
            # Downside that *args can't be used instead of kwargs
            # We can check for args in func, and use that to map keys
            # to arg index, but we're don't need that desperately, and would clutter
            def replacing_func(*a,**kwargs):
                cachekey = "%".join([
                    "^".join(map(str,kwargs[arg])) if isinstance(kwargs[arg],(tuple,list)) else str(kwargs[arg])
                    for arg
                    in cache_args
                ])
                cache = Cache.get(func.__name__,cachekey)
                if cache is not None:
                    return cache.get()
                data = func(**kwargs)
                _cache_for = cache_for(**kwargs) if callable(cache_for) else cache_for
                Cache.put(func.__name__,cachekey,CacheItem(data,_cache_for))
                return data
            return replacing_func
        return decorator