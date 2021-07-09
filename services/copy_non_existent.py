def main():
    from library.postgres import DB
    from core.types.Address import Address
    from core.Token.Token import Token
    from core.sources.BscScanApi import BscScanApi
    from concurrent.futures import ThreadPoolExecutor
    from library.timer import timer

    def insert_token(data: tuple, db: DB):
        address,name,symbol,decimals,total_supply,standard = data
        if name == "Pancake LPs": return
        
        address = Address(address)
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
        

    with DB() as db:
        bscscan_api = BscScanApi()
        tokens = db.get_all("""
        SELECT temp_tokens_external.* FROM temp_tokens_external
        LEFT JOIN tokens ON tokens.address = temp_tokens_external.address
        WHERE tokens.address IS NULL
        """)
        
        with timer("Update Holders") as increment:
            for p in range(0,len(tokens),100):
                subset = tokens[p:p+100]
                with ThreadPoolExecutor(max_workers=4) as exec:
                    for data in subset:
                        exec.submit(insert_token,data=data,db=db)
                
                increment(len(subset))