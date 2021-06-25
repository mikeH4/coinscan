def main():
    from core.sources.ScannerApi import ScannerApi
    from library.Repeater import Repeater
    from core.misc.TokenPrices import TokenPrices
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*10)
        scanner_api = ScannerApi()

        while True:
            with repeater.manager():
                data = scanner_api.prices()

                TokenPrices.completely_absolutely_replace(data)
                
                print("Replaced all data")