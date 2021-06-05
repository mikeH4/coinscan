from library.BaseModel import BaseModelMetaClass
from library.ratelimit import limits, sleep_and_retry
import json
from urllib.parse import urljoin

from library.requests import get

class BaseSourceMetaClass(type):
    def __init__(cls, name, bases, namespace, **kwargs) -> None:
        if len(bases) < 1:
            return None
        if str(bases[0]) != "<class 'core.sources.BaseSource.BaseSource'>":
            return None

        if cls.url is None:
            raise NotImplementedError("Class is invalid, url must be present")
        

        cls.request = sleep_and_retry(
            limits(
                calls=cls.limit_calls,
                period=cls.limit_period
            )(cls.request)
        )

# Abstract Clas
class BaseSource(metaclass=BaseSourceMetaClass):
    url = None
    limit_calls = 1
    limit_period = 1

    @staticmethod
    def parse_soup_json(soup,selector):
        script_content = soup.select(selector)[0].string
        return json.loads(script_content)

    def request(self,path):
        headers = {}
        if self.agent is not None:
            headers["User-Agent"] = self.agent
        return get(urljoin(self.url,path),proxy=self.proxy,headers=headers)

    def get():
        raise NotImplementedError("get() must be defined in class")