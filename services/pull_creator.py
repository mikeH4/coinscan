def main():
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Token.TokenMeta import TokenMeta
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*1,max=60*5)
        bscscan = BscScan()

        limit_stretch = 30
        while True:
            with repeater.manager():
                addresses = [
                    token_meta.address
                    for token_meta
                    in TokenMeta.where_is_none("creator",limit=limit_stretch)
                ]
                addresses_len = len(addresses)
                if addresses_len <= 0:
                    limit_stretch += 30

                for i,address in enumerate(addresses):
                    creator,creation_tx = bscscan.creation(
                        address=address
                    )
                    TokenMeta.update(
                        address=address,
                        db=db,
                        creator=str(creator),
                        creation_tx=str(creation_tx)
                    )
                    db.conn.commit()

                    print(f"{i+1}/{addresses_len} Creator added for {address}")
                
                print("Ended loop, no timeout")