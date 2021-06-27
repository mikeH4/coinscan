def main():
    from time import time
    
    from core.sources.ScannerApi import ScannerApi
    from library.Repeater import Repeater
    from core.misc.Pairs import Pairs
    from core.types.Address import Address
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=5)
        scanner_api = ScannerApi()

        # 2.5 min max
        while repeater.loop():
            pairs_to_add = scanner_api.token_pairs_count() - Pairs.count()
            for offset in range(0,pairs_to_add,100):
                data = scanner_api.token_pairs(limit=100,offset=offset)
                data_len = len(data)

                for i,token_pair in enumerate(data):
                    token,pair = token_pair
                    token = Address(token)
                    pair = Address(pair)

                    Pairs(token=token, pair=pair, updated=time()).insert_or_ignore()

                    print(f"{i+1}/{data_len} Pair Inserted/Ignored")