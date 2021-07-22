def main():
    from core.sources.ScannerApi import ScannerApi
    from library.Repeater import Repeater
    from core.sources.BscScanApi import BscScanApi
    from core.Token.Token import Token
    from core.types.Address import Address
    from library.postgres import DB

    
    with DB() as db:
        repeater = Repeater(min=15,max=60*2.5)
        bscscan_api = BscScanApi()
        scanner_api = ScannerApi()

        existing_addrs = []

        while repeater.loop():
            data = scanner_api.new()
            data_len = len(data)

            addresses = [row["address"] for row in data]
            
            if len(existing_addrs) == 0:
                print("Fetched Existing From")
                existing_addrs = Token.existing_from(addresses,db)
            elif len(existing_addrs) > 5000:
                # Just so memory doesn't escape
                existing_addrs = existing_addrs[5000:]

            for i,token_data in enumerate(data):
                if token_data["address"] in existing_addrs:
                    continue
                existing_addrs.append(token_data["address"])

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
                    db=db
                )

                print(f"{i+1}/{data_len} Token Inserted")

                if repeater.should_repeat():
                    break