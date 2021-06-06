from library.BaseSource import BaseSource
from bs4 import BeautifulSoup

class CoinMarketCap(BaseSource):
    url = "https://coinmarketcap.com/"

    limit_calls = 1
    limit_period = 5
    
    def new(self):
        res = self.request(f"/new/")
        soup = BeautifulSoup(res.text,"html.parser")
        data = self.parse_soup_json(soup,"#__NEXT_DATA__")
        raw = data["props"]["initialState"]["cryptocurrency"]["new"]["data"]
        return raw

class CoinMarketCapInternalApi(BaseSource):
    url = "https://api.coinmarketcap.com"

    limit_calls = 1
    limit_period = 5

    def single(self, slug):
        res = self.request(
            f"/data-api/v3/cryptocurrency/detail",
            params=dict(
                slug=slug,
                langCode="en",
                aux="status",
            )
        )
        return res.json()["data"]


class CoinMarketCapProApi(BaseSource):
    url = "https://pro-api.coinmarketcap.com/"

    limit_calls = 1
    limit_period = 5

    def all(self):
        ls = []
        page = 0
        while page * 5000 == len(ls):
            res = self.request(
                f"/v1/cryptocurrency/listings/latest",
                params=dict(
                    CMC_PRO_API_KEY=self.apikey,
                    limit=5000,
                    start=(page*5000)+1
                )
            )
            ls += res.json()["data"]
            page += 1
        return ls