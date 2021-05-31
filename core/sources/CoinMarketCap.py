from core.sources.BaseSource import BaseSource

class CoinMarketCap(BaseSource):
    url = "https://pro-api.coinmarketcap.com/"
    apikey = "908c403f-561a-44d7-9ebe-c06ad90ae630"

    agent = None
    proxy = None

    limit_calls = 1
    limit_period = 1
    
    def listings(self):
        ls = []
        page = 0
        while page * 5000 == len(ls):
            res = self.request(f"/v1/cryptocurrency/listings/latest?CMC_PRO_API_KEY={self.apikey}&limit=5000&start={(page*5000)+1}")
            ls += res.json()["data"]
            page += 1
        return ls