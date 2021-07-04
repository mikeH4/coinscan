def main():
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Token.TokenMeta import TokenMeta
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=12,max=60*2)
        bscscan = BscScan()

        while repeater.loop():
            addresses = bscscan.recently_verified()
            addresses_len = len(addresses)

            for i,address in enumerate(addresses):
                TokenMeta.update(
                    address=address,
                    db=db,
                    source_verified=True
                )
                db.conn.commit()

                print(f"{i+1}/{addresses_len} has been verifed")