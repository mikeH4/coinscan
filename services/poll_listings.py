from library.Repeater import Repeater
from core.sources.CoinGecko import CoinGecko
from core.sources.CoinMarketCap import CoinMarketCap

def main():
    repeater = Repeater(min=60*30)

    while repeater.loop():
        CoinMarketCap().update_token_listings()
        CoinGecko().update_token_listings()

        print("Updated Listings")

# In the future, could add option for correlation between tokens based on listing platforms
# with internal field for reference