from library.request import get


class NoProxy:
    @classmethod
    def request(cls, _class, url, **kwargs):
        if "param_from_proxy" in kwargs:
            del kwargs["param_from_proxy"]
        return get(url,**kwargs)