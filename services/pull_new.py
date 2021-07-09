from library.Repeater import Repeater

def main():
    from core.sources.BscScanApi import BscScanApi
    from core.Token.Token import Token
    from core.types.Address import Address
    from library.postgres import DB
    from core.sources.TokenFomo import TokenFomo

    with DB() as db:
        repeater = Repeater(min=45,max=60*1.5)
        bscscan_api = BscScanApi()
        tokenfomo = TokenFomo()

        while repeater.loop():
            data = tokenfomo.get()

            addresses = [row[1] for row in data if row[0] == "BSC"]
            existing_addrs = Token.existing_from(addresses,db)

            data_len = len(data)

            for i,token_data in enumerate(data):
                chain,address,name,symbol,block_time = token_data
                address = Address(address)
                if chain != "BSC":
                    continue

                if str(address) in existing_addrs:
                    continue

                Token.insert_with_source(
                    bscscan_api=bscscan_api,
                    address=address,
                    name=name,
                    symbol=symbol,
                    block_time=block_time,
                    db=db
                )

                print(f"{i+1}/{data_len} Token Inserted")

                if repeater.should_repeat():
                    # Scan from TokenFomo again
                    break