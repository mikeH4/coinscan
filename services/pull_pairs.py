def main():
    from time import time
    
    from core.sources.ScannerApi import ScannerApi
    from library.Repeater import Repeater
    from core.misc.Pairs import Pairs
    from core.types.Address import Address
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*5)
        scanner_api = ScannerApi()

        limit = 200

        # 2.5 min max
        while repeater.loop():
            existing_pairs = Pairs.count(db=db)
            all_pairs = scanner_api.token_pairs_count()
            print("All Pairs",all_pairs)

            print("Pairs to add:",all_pairs - existing_pairs)

            for offset in range(existing_pairs,all_pairs,limit):
                print("From:",offset)
                data = scanner_api.token_pairs(limit=limit,offset=offset)
                data_len = len(data)

                for i,token_pair in enumerate(data):
                    token,pair = token_pair
                    token = Address(token)
                    pair = Address(pair)

                    Pairs(token=token, pair=pair, updated=time()).insert_or_ignore(db=db)

                    print(f"{i+1}/{data_len} Pair Inserted/Ignored: {pair}")
                
                db.conn.commit()