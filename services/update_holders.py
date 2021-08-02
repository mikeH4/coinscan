from concurrent.futures.thread import ThreadPoolExecutor
from core.Wallets.WalletHoldings import WalletHoldings
from core.Wallets._inter_pull_and_update import pull_and_update
from library.Repeater import Repeater
from library.postgres import DB
from library.timer import timer

def main():
    with DB(auto_commit=False) as db:
        repeater = Repeater(min=60*3)
        
        while repeater.loop():
            with timer("Update Holders") as increment:
                address_objects = WalletHoldings.not_updated(db=db)
                if len(address_objects) < 1:
                    print("Breaking")
                    break
                print(len(address_objects))

                with ThreadPoolExecutor(max_workers=4) as exec:
                    for address, pair_address in address_objects:
                        pair_types: tuple = (None,) if pair_address is None else (None, pair_address)

                        for pair in pair_types:
                            # pull_and_update(chain=address.chain,token_address=address.address,pair_address=pair,db=db)
                            exec.submit(
                                pull_and_update,
                                chain=address.chain,
                                token_address=address.address,
                                pair_address=pair,
                                db=db
                            )

                db.conn.commit()
                increment(len(address_objects))
