from ratelimit import limits, sleep_and_retry
import json
from urllib.parse import urljoin

from library.requests import get

# Abstract Clas
class BaseSource:
    url = None
    limit_calls = 1
    limit_period = 1

    def __new__(cls,*args,**kwargs):
        if cls.url is None:
            raise NotImplementedError("Class is invalid, url must be present")
        
        cls.request = sleep_and_retry(
            limits(
                calls=cls.limit_calls,
                period=cls.limit_period
            )(BaseSource.request)
        )

        _new = BaseSource.__new__
        del BaseSource.__new__

        created = cls(*args,**kwargs)

        BaseSource.__new__ = _new

        return created

    @staticmethod
    def parse_soup_json(soup,selector):
        script_content = soup.select(selector)[0].string
        return json.loads(script_content)

    def request(self,path):
        return get(urljoin(self.url,path))

    def get():
        raise NotImplementedError("get() must be defined in class")