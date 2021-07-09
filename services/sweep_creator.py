def main():
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Token.TokenMeta import TokenMeta
    from library.postgres import DB

    with DB() as db:
        repeater = Repeater(min=60*1,max=60*5)
        bscscan = BscScan()

        while repeater.loop():
            addresses = [
                token_meta.address
                for token_meta
                in TokenMeta.where_is_none("creator",limit=30)
            ]
            addresses_len = len(addresses)

            for i,address in enumerate(addresses):
                c = bscscan.creation(
                    address=address
                )
                if c is None:
                    TokenMeta.update(
                        address=address,
                        db=db,
                        creator="",
                        creation_tx=""
                    )
                    print(f"{i+1}/{addresses_len} Empty Creator added for {address}")
                    continue
                
                creator,creation_tx = c
                TokenMeta.update(
                    address=address,
                    db=db,
                    creator=str(creator),
                    creation_tx=str(creation_tx)
                )
                print(f"{i+1}/{addresses_len} Creator added for {address}")
        
            print("Commit Creators")
            db.conn.commit()