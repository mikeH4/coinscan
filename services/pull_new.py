from library.Repeater import Repeater

def main():
    from core.sources.BscScanApi import BscScanApi
    from core.Token.Token import Token
    from core.types.Address import Address
    from library.postgres import DB
    from core.sources.TokenFomo import TokenFomo

    with DB("tokens") as db:
        repeater = Repeater(min=45,max=60*1.5)
        bscscan_api = BscScanApi()
        tokenfomo = TokenFomo()

        while True:
            with repeater.manager():
                data = tokenfomo.get()

                addresses = [row["addr"] for row in data]
                existing_addrs = Token.existing_from(addresses,db)

                data_len = len(data)

                for i,token_data in enumerate(data):
                    if token_data["chainId"] != "BSC":
                        continue
                    if token_data["addr"] in existing_addrs:
                        continue
                    address = Address(token_data["addr"])

                    Token.insert_with_source(
                        bscscan_api=bscscan_api,
                        address=address,
                        name=token_data["name"],
                        symbol=token_data["symbol"],
                        block_time=token_data["blockTime"],
                    )

                    print(f"{i+1}/{data_len} Token Inserted")

                    if repeater.should_repeat():
                        # Scan from TokenFomo again
                        break