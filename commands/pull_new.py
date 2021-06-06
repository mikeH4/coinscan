from core.sources.BscScanApi import BscScanApi
from time import sleep, time
from core.Token.Token import Token
from core.types.Address import Address
from library.postgres import DB
from core.sources.TokenFomo import TokenFomo

def get_existing(of:list, db:DB):
    of = list(map(str,of))
    placeholder = db.placeholder(len(of))
    sql = f"SELECT address FROM tokens WHERE address IN ({placeholder})"
    addrs = [row[0] for row in db.get_all(sql,of)]
    return addrs

tokenfomo_max_update = 60*1.5
tokenfomo_min_update = 45*1


with DB("tokens") as db:
    bscscan_api = BscScanApi()

    last_tokenfomo = 0

    while True:
        sleep_for = tokenfomo_min_update - (time() - last_tokenfomo)
        if sleep_for > 0:
            print("Sleep for",sleep_for)
            sleep(sleep_for)

        tokenfomo = TokenFomo()
        data = tokenfomo.get()

        last_tokenfomo = time()

        addresses = [row["addr"] for row in data]
        existing_addrs = get_existing(addresses,db)

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

            if (time() - last_tokenfomo) > tokenfomo_max_update:
                # Scan from TokenFomo again
                break
        print("Ended loop, no timeout")