from library.RequestManager.CentralProxy import CentralProxy
import json
from urllib.parse import urljoin

class BaseSourceMetaClass(type):
    def __init__(cls, name, bases, namespace, **kwargs) -> None:
        if len(bases) < 1:
            return None
        if str(bases[0]) != "<class 'library.BaseSource.BaseSource'>":
            return None

        if cls.url is None:
            raise NotImplementedError("Class is invalid, url must be present")

# Abstract Class
class BaseSource(metaclass=BaseSourceMetaClass):
    url = None
    limit_calls = 1
    limit_period = 1
    param_from_proxy={}

    # Only use in exceptional cases
    limit_bypass = False

    request_manager = CentralProxy

    @staticmethod
    def inherits(_class):
        if not issubclass(_class,BaseSource):
            raise TypeError(f"{_class.__name__} does not inherit from BaseSource")

    @staticmethod
    def parse_soup_json(soup,selector):
        script_content = soup.select(selector)[0].string
        return json.loads(script_content)

    def request(self,path,params={},headers={},cookies={},json={}):
        # Sleep and retry
        while True:
            kwds = dict(
                url=urljoin(self.url,path),
                params=params,
                headers=headers,
                cookies=cookies,
                json=json,
            )
            return self.request_manager.request(
                **kwds,
                _class=self.__class__
            )