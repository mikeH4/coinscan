def main():
    from core.sources.ScannerApi import ScannerApi
    from library.Repeater import Repeater
    from core.Token.Token import Token
    from core.types.Address import Address
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=5)
        scanner_api = ScannerApi()

        # 2.5 min max
        while repeater.loop():
            data = scanner_api.token_pairs()

            for i,token_data in enumerate(data):
                if token_data["address"] in existing_addrs:
                    continue
                address = Address(token_data["address"])
                if token_data["name"] == "Pancake LPs":
                    continue
                if token_data["block"] is not None and token_data["block_time"] is None:
                    # Still waiting to be processed, ignore for now
                    print(f"Waiting for {address}")
                    continue

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