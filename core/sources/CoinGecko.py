from core.sources.BaseSource import BaseSource

class CoinGecko(BaseSource):
    url = "https://api.coingecko.com"

    agent = None
    proxy = None

    limit_calls = 1
    limit_period = 1
    
    def listings(self):
        res = self.request(f"/api/v3/coins/list?include_platform=true")
        return res.json()