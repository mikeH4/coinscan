

def main():
    from core.sources.BscScanApi import BscScanApi
    from core.Token.ViewableToken import ViewableToken
    from core.Token.Token import Token
    from library.postgres import DB

    with DB("tokens") as db:
        bscscan_api = BscScanApi()

        tokens = ViewableToken.last_day(db=db)
        tokens_len = len(tokens)

        for i,token in enumerate(tokens):
            total_supply = bscscan_api.total_supply(token.address)
            if total_supply == 0:
                print(f"{token.address} has total_supply 0, deleting")
                Token.permanent_delete(token.address,db=db)
                db.conn.commit()

            print(f"{i+1}/{tokens_len} tokens checked: {token.address}")