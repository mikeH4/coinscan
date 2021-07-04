from library.timer import timer


def main():
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Holders.Holders import Holders
    from core.Token.TokenMeta import TokenMeta
    from core.Token.Query import Query
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*6,max=60*10)
        bscscan = BscScan()

        while repeater.loop():
            addresses = [
                token.address
                for token
                in Query.get_frequent_addresses()
            ]
            addresses_len = len(addresses)

            for i,address in enumerate(addresses):
                total,top = bscscan.holders(
                    address=address
                )
                with timer("Update TokenMeta"):
                    TokenMeta.update(
                        address=address,
                        db=db,
                        holders=total
                    )
                with timer("Delete Holders"):
                    Holders.delete_all(contract=address,db=db)
                
                for holder,address_info in top:
                    with timer(f"Insert Or update holder {holder.holder}"):
                        holder.insert_or_update(db=db)
                    with timer(f"Insert Or update address info {holder.holder}"):
                        address_info.insert(db=db,replace=True)

                with timer("Commit Holders"):
                    db.conn.commit()
                print(f"{i+1}/{addresses_len} Token Holders Updated")

                if repeater.should_repeat():
                    break