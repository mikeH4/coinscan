from concurrent.futures.thread import ThreadPoolExecutor
from core.Wallets.WalletHoldings import WalletHoldings
from core.Wallets._inter_pull_and_update import pull_and_update
from library.Repeater import Repeater
from library.database.postgres import DB
from library.timer import timer

def main():
    with DB(auto_commit=False) as db:
        repeater = Repeater(min=60*3)
        limit = 30
        
        while repeater.loop():
            with timer("Update Holders") as increment:
                address_objects = WalletHoldings.not_updated(db=db)
                print("len",len(address_objects))
                if len(address_objects) < 1:
                    print("Breaking")
                    break

                for offset in range(0,len(address_objects),limit):
                    slice = address_objects[offset:offset+limit]
                    with ThreadPoolExecutor(max_workers=4) as exec:
                        for address_obj, pair_address_hash in slice:
                            pair_types: tuple = (None,) if pair_address_hash is None else (None, pair_address_hash)
                            for pair in pair_types:
                                exec.submit(
                                    pull_and_update,
                                    chain=address_obj.chain,
                                    token_address=address_obj.address,
                                    pair_address=pair,
                                    db=db
                                )
                    
                    print(f"Commit {offset}-{limit+offset} of {len(address_objects)}")
                    db.conn.commit()
                    increment(len(slice))
