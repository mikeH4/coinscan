def main():
    from core.misc.Pairs import Pairs
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Holders.Holders import Holders
    from core.Token.TokenMeta import TokenMeta
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*5)
        bscscan = BscScan()

        while repeater.loop():
            while True:
                pairs = Pairs.unknown_pairs(db=db,limit=100)
                pairs_len = len(pairs)
                if pairs_len < 1:
                    break

                for i,address in enumerate(pairs):
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
                    print(f"{i+1}/{pairs_len} Pair Holders Updated")