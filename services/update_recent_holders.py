from library.timer import timer


def main():
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Holders.Holders import Holders
    from core.Token.TokenMeta import TokenMeta
    from core.Token.Query import Query
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*8,max=60*10)
        bscscan = BscScan()

        while repeater.loop():
            addresses = [
                token.address
                for token
                in Query.get_frequent_addresses(limit=50)
            ]
            addresses_len = len(addresses)

            for i,address in enumerate(addresses):
                Holders.update_with_pull(
                    address=address,
                    bscscan=bscscan,
                    db=db
                )
                with timer("Commit Holders"):
                    db.conn.commit()

                print(f"{i+1}/{addresses_len} Token Holders Updated")

                if repeater.should_repeat():
                    break