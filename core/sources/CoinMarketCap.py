from core.sources.BaseSource import BaseSource
from urllib.parse import urljoin
from library.requests import get
from bs4 import BeautifulSoup
from library.ratelimit import limits,sleep_and_retry

class CoinMarketCap(BaseSource):
    url = "https://pro-api.coinmarketcap.com/"
    apikey = "908c403f-561a-44d7-9ebe-c06ad90ae630"

    home_url = "https://coinmarketcap.com/"
    internal_api_url = "https://api.coinmarketcap.com"

    agent = None
    proxy = None

    limit_calls = 1
    limit_period = 1
    
    def all(self):
        ls = []
        page = 0
        while page * 5000 == len(ls):
            res = self.request(
                f"/v1/cryptocurrency/listings/latest?CMC_PRO_API_KEY={self.apikey}&limit=5000&start={(page*5000)+1}",
                domain=self.url
            )
            ls += res.json()["data"]
            page += 1
        return ls

    @limits(calls=1,period=5)
    def request(self,path,domain):
        return get(urljoin(domain,path))

    def new(self):
        res = self.request(f"/new/",domain=self.home_url)
        soup = BeautifulSoup(res.text,"html.parser")
        data = self.parse_soup_json(soup,"#__NEXT_DATA__")
        raw = data["props"]["initialState"]["cryptocurrency"]["new"]["data"]
        return raw
    
    def single(self, slug):
        res = self.request(
            f"/data-api/v3/cryptocurrency/detail?slug={slug}&langCode=en&aux=status",
            domain=self.internal_api_url
        )
        return res.json()["data"]
