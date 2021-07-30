from library.request import get


class NoProxy:
    @classmethod
    def request(cls, _, url, **kwargs):
        return get(url,**kwargs)