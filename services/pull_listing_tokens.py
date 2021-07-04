def main():
    from core.sources.ScannerApi import ScannerApi
    from core.sources.BscScanApi import BscScanApi
    from library.Repeater import Repeater
    from core.Token.Token import Token
    from core.misc.Listing import Listing
    from core.types.Address import Address
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=60*2)
        bscscan_api = BscScanApi()
        scanner_api = ScannerApi()

        while repeater.loop():
            addresses = Listing.get_addresses_not_inserted(db=db)
            addresses_len = len(addresses)
            print(f"Search for {addresses_len} addresses")

            data = scanner_api.get_addresses(addresses)
            data_len = len(data)

            print(f"{addresses_len-data_len} tokens not in response")

            for i,token_data in enumerate(data):
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
                    db=db
                )

                print(f"{i+1}/{data_len} Token Inserted")