from core.Address import Address
from core.Token.TokenStats import TokenStats
from library.database.postgres import DB
from core.sources.ScannerApi import ScannerApi
from core.sources.BscScanApi import ChainScanApi
from core.types.AddressHash import AddressHash
from core.Token.TokenMeta import TokenMeta
from core.types.db_types import ChainEnum, bigint
from library.Repeater import Repeater

def main():
    with DB(auto_commit=False) as db:
        repeater = Repeater(min=10,max=int(60*2.5))
        scanner_api = ScannerApi()

        existing_addrs: dict[ChainEnum,list[AddressHash]] = {
            ChainEnum("eth"): [],
            ChainEnum("bsc"): [],
        }

        while repeater.loop():
            for chain in ["eth","bsc"]:
                chain = ChainEnum(chain)
                data = scanner_api.new(chain)
                data_len = len(data)

                addresses = [AddressHash(row["address"]) for row in data]
                
                if len(existing_addrs[chain]) == 0:
                    print("Fetched Existing is 0")
                    print("First 5",addresses[:5])
                    existing_addrs[chain] = Address.addresses_from(chain=chain, addresses=addresses, db=db)
                elif len(existing_addrs[chain]) > 5000:
                    # Just so memory doesn't escape
                    existing_addrs[chain] = existing_addrs[chain][5000:]


                for i,token_data in enumerate(data):
                    address = AddressHash(token_data["address"])

                    if address in existing_addrs[chain]: continue
                    existing_addrs[chain].append(address)

                    decimals = token_data["decimals"]
                    total_supply = token_data["total_supply"]/(10**decimals)
                    
                    # if not token_data["block_time"]:
                    #     print(chain,address,"block_time is not ->",token_data["block_time"])
                    #     continue

                    id = TokenMeta(
                        id=bigint(0),
                        name=token_data["name"],
                        symbol=token_data["symbol"],
                        decimals=decimals,
                        created_time=token_data["block_time"],
                        source_verified=ChainScanApi(chain).source_code(address=address) is not None
                    ).insert_or_update(
                        chain=chain,
                        token_address=address,
                        db=db
                    )

                    TokenStats(
                        id=id,
                        total_supply=total_supply
                    )._upsert_by_id(
                        dont_update=["circulating","price_change","holders","liquidity"],
                        db=db
                    )

                    print(f"{i+1}/{data_len} Token Inserted")
                    repeater.commit(db)

                    if repeater.should_repeat():
                        break

                db.conn.commit()