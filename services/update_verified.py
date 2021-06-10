def main():
    from library.Repeater import Repeater
    from core.sources.BscScanApi import BscScanApi
    from core.Token.TokenMeta import TokenMeta
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=0,max=60*10)
        bscscan_api = BscScanApi()

        while True:
            with repeater.manager():
                addresses = TokenMeta.get_addresses(
                    limit=None,
                    where_cond="WHERE token_meta.source_verified IS NOT TRUE"
                )
                addresses_len = len(addresses)

                for i,address in enumerate(addresses):
                    source_verified = (bscscan_api.source_code(
                        address=address
                    ) is not None)
                    print(source_verified)
                    TokenMeta.update(
                        address=address,
                        db=db,
                        source_verified=source_verified
                    )
                    db.conn.commit()

                    print(f"{i+1}/{addresses_len} Token Updated")