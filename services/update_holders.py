from core.Holders.Holders import Holders

def main():
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Token.TokenMeta import TokenMeta
    from core.Token.ViewableToken import ViewableToken
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*3,max=60*4)
        bscscan = BscScan()

        while True:
            with repeater.manager():
                addresses = [
                    token.address
                    for token
                    in ViewableToken.get_latest()
                ]
                addresses_len = len(addresses)

                for i,address in enumerate(addresses):
                    total,top = bscscan.holders(
                        address=address
                    )
                    print(total)
                    TokenMeta.update(
                        address=address,
                        db=db,
                        holders=total
                    )
                    Holders.delete_all(contract=address)
                    for holder in top:
                        holder.insert_or_update(db=db)

                    print(f"{i+1}/{addresses_len} Token Holders Updated")

                    if repeater.should_repeat():
                        break
                
                print("Ended loop, no timeout")