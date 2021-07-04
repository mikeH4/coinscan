def main():
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Holders.Holders import Holders
    from core.Holders.HoldersPulled import HoldersPulled
    from library.postgres import DB
    from library.timer import timer
    from concurrent.futures import ThreadPoolExecutor

    with DB("tokens",auto_commit=False) as db:
        repeater = Repeater(min=60*3)
        bscscan = BscScan()
        
        while repeater.loop():
            with timer("Update Holders") as increment:
                while True:
                    addresses = HoldersPulled.not_updated_at_all(limit=100)
                    if len(addresses) < 1:
                        addresses = HoldersPulled.not_updated_recently(limit=100)
                    
                    addresses_len = len(addresses)
                    if addresses_len < 1:
                        print("Breaking")
                        break

                    with ThreadPoolExecutor(max_workers=3) as exec:
                        for address in addresses:
                            exec.submit(Holders.update_with_pull,address=address,bscscan=bscscan,db=db)

                    db.conn.commit()
                    increment(addresses_len)
