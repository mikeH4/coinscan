def main():
    from core.misc.Pairs import Pairs
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Holders.Holders import Holders
    from library.postgres import DB
    from library.timer import timer
    from concurrent.futures import ThreadPoolExecutor

    with DB("tokens",auto_commit=False) as db:
        repeater = Repeater(min=60*5)
        bscscan = BscScan()

        while repeater.loop():
            with timer("Pair Holders") as increment:
                while True:
                    pairs = Pairs.unknown_pairs(db=db,limit=100)
                    pairs_len = len(pairs)
                    if pairs_len < 1:
                        print("Breaking")
                        break

                    with ThreadPoolExecutor(max_workers=3) as exec:
                        for address in pairs:
                            exec.submit(Holders.update_with_pull,address=address,bscscan=bscscan,db=db)

                    db.conn.commit()
                    increment(pairs_len)
