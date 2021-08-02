from core.Wallets.ViewableWalletHoldings import ViewableWalletHoldings
from core.Wallets.WalletHoldings import WalletHoldings
from library.Repeater import Repeater
from library.postgres import DB
from library.timer import timer
from concurrent.futures import ThreadPoolExecutor

def main():
    with DB(auto_commit=False) as db:
        repeater = Repeater(min=60*3)
        
        while repeater.loop():
            with timer("Update Holders") as increment:
                while True:
                    addresses = ViewableWalletHoldings.not_updated(db=db)
                    if len(addresses) < 1:
                        print("Breaking")
                        break

                    with ThreadPoolExecutor(max_workers=4) as exec:
                        for address in addresses:
                            exec.submit(
                                WalletHoldings.pull_and_update,
                                token_address=address,
                                db=db
                            )

                    db.conn.commit()
                    increment(len(addresses))
