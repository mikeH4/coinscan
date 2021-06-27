def main():
    from core.misc.Pairs import Pairs
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Holders.Holders import Holders
    from core.Token.TokenMeta import TokenMeta
    from library.postgres import DB
    from time import time
    from concurrent.futures import ThreadPoolExecutor

    def update_holder(address,db:DB):
        total,top = bscscan.holders(
            address=address
        )
        TokenMeta.update(
            address=address,
            db=db,
            holders=total
        )
        Holders.delete_all(contract=address,db=db)
        for holder,address_info in top:
            holder.insert_or_update(db=db)
            address_info.insert(db=db,replace=True)

        db.conn.commit()

    with DB("tokens") as db:
        repeater = Repeater(min=60*5)
        bscscan = BscScan()

        while repeater.loop():
            start = time()
            total_sweeped = 0
            while True:
                pairs = Pairs.unknown_pairs(db=db,limit=100)
                pairs_len = len(pairs)
                if pairs_len < 1:
                    print("Breaking")
                    break

                with ThreadPoolExecutor(max_workers=3) as exec:
                    for i,address in enumerate(pairs):
                        exec.submit(update_holder,address=address, db=db)
                
                total_sweeped += pairs_len
                print(f"{total_sweeped} of all Pair Holders Sweeped, Avg {total_sweeped/(time() - start)*60} per min")
                    
