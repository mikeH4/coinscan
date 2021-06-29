def main():
    from library.postgres import DB
    from core.types.Address import Address
    from core.Token.Token import Token
    from core.sources.BscScanApi import BscScanApi

    with DB("tokens") as db:
        bscscan_api = BscScanApi()
        tokens = db.get_all("""
        SELECT temp_tokens_external.* FROM temp_tokens_external
        LEFT JOIN tokens ON tokens.address = temp_tokens_external.address
        WHERE tokens.address IS NULL
        """)
        
        tokens_len = len(tokens)

        for i,data in enumerate(tokens):
            address,name,symbol,decimals,total_supply,standard = data

            address = Address(address)
            if name == "Pancake LPs":
                continue

            total_supply = float(total_supply)/(10**decimals)
            Token.insert_with_source(
                bscscan_api=bscscan_api,
                address=address,
                name=name,
                symbol=symbol,
                decimals=decimals,
                total_supply=total_supply,
                db=db
            )

            print(f"{i+1}/{tokens_len} Token Inserted")