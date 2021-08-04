from core.types.db_types import ChainEnum
from core.sources.ScannerApi import ScannerApi
from library.Repeater import Repeater
from core.Token.TokenStats import TokenStats

def main():
    repeater = Repeater(min=60*10)
    scanner_api = ScannerApi()

    while repeater.loop():
        for chain in ["bsc"]:
            chain = ChainEnum(chain)
            data = scanner_api.prices(chain)
            TokenStats.replace_price_data(
                chain=chain,
                data=data
            )
        
        print("Replaced all data")