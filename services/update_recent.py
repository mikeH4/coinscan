def main():
    from library.Repeater import Repeater
    from core.sources.BscScanApi import BscScanApi
    from core.Token.TokenMeta import TokenMeta
    from core.Token.ViewableToken import ViewableToken
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*2,max=60*3)
        bscscan_api = BscScanApi()

        while True:
            with repeater.manager():
                addresses = [
                    token.address
                    for token
                    in ViewableToken.get_latest()
                ]
                addresses_len = len(addresses)

                for i,address in enumerate(addresses):
                    source_verified = (bscscan_api.source_code(
                        address=address
                    ) is not None)
                    TokenMeta.update(
                        address=address,
                        db=db,
                        source_verified=source_verified
                    )

                    print(f"{i+1}/{addresses_len} Token Updated")

                    if repeater.should_repeat():
                        break
                
                print("Ended loop, no timeout")