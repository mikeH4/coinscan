def main():
    from core.sources.ScannerApi import ScannerApi
    from library.Repeater import Repeater
    from core.sources.BscScanApi import BscScanApi
    from core.Token.Token import Token
    from core.types.Address import Address
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*1.5,max=60*5)
        bscscan_api = BscScanApi()
        scanner_api = ScannerApi()

        while True:
            with repeater.manager():
                data = scanner_api.newly_added()

                addresses = [row["address"] for row in data]
                existing_addrs = Token.existing_from(addresses,db)

                data_len = len(data)

                for i,token_data in enumerate(data):
                    if token_data["address"] in existing_addrs:
                        continue
                    address = Address(token_data["address"])

                    decimals = token_data["decimals"]
                    total_supply = token_data["total_supply"]/(10**decimals)
                    Token.insert_with_source(
                        bscscan_api=bscscan_api,
                        address=address,
                        name=token_data["name"],
                        symbol=token_data["symbol"],
                        decimals=decimals,
                        total_supply=total_supply,
                        block_time=token_data["block_time"],
                        dont_update_meta=["block_time"]
                    )

                    print(f"{i+1}/{data_len} Token Inserted")

                    if repeater.should_repeat():
                        # Scan from TokenFomo again
                        break