from library.request import get


class NoProxy:
    @classmethod
    def request(cls, _class, url, **kwargs):
        return get(url,**kwargs)