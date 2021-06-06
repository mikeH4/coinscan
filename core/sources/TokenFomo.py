from core.sources.BaseSource import BaseSource
from bs4 import BeautifulSoup

class TokenFomo(BaseSource):
    url = "https://tokenfomo.io/"

    def __init__(self,**kwds) -> None:
        for attr in ["proxy","agent"]:
            setattr(self,attr,kwds.get(attr,None))

    def get(self):
        res = self.request("/")
        data = self.parse_soup_json(
            BeautifulSoup(res.text,"html.parser"),
            "script#__NEXT_DATA__"
        )["props"]["pageProps"]["tokens"]

        return data