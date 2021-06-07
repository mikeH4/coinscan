from library.BaseSource import BaseSource

class CoinGecko(BaseSource):
    url = "https://api.coingecko.com"

    limit_calls = 1
    limit_period = 1
    
    def listings(self):
        res = self.request(f"/api/v3/coins/list",params=dict(
            include_platform="true"
        ))
        try:
            return res.json()
        except ValueError:
            print("CoinGecko JSON error")
            print(res.text)
            return []