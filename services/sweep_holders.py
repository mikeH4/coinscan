
def main():
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Holders.Holders import Holders
    from core.Holders.AddressInfo import AddressInfo
    from core.Token.TokenMeta import TokenMeta
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*1,max=60*4)
        bscscan = BscScan()

        while True:
            with repeater.manager():
                addresses = AddressInfo.unknown_holder_contracts(db=db,limit=50)
                addresses_len = len(addresses)

                for i,address in enumerate(addresses):
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
                    print(f"{i+1}/{addresses_len} Token Holders Updated")

                    if repeater.should_repeat():
                        break