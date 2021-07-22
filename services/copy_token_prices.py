def main():
    from core.sources.ScannerApi import ScannerApi
    from library.Repeater import Repeater
    from core.misc.TokenPrices import TokenPrices

    repeater = Repeater(min=60*10)
    scanner_api = ScannerApi()

    while repeater.loop():
        data = scanner_api.prices()
        TokenPrices.completely_absolutely_replace(data)

        
        print("Replaced all data")