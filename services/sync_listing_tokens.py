from core.Token.TokenStats import TokenStats
from core.Token.TokenMeta import TokenMeta
from core.types.AddressHash import AddressHash
from core.types.db_types import ChainEnum, bigint
from core.Token.ViewableTokenListings import ViewableTokenListings
from core.sources.ScannerApi import ScannerApi
from library.database.postgres import DB

def main():
    scanner_api = ScannerApi()
    
    with DB() as db:
        for chain in ChainEnum.enum_opts:
            chain = ChainEnum(chain)
            addresses = [listing.token_address for listing in ViewableTokenListings.unlisted(chain=chain,db=db)]
            print(f"Search for {len(addresses)} addresses")

            data = scanner_api.get_addresses(chain, addresses=addresses)
            data_len = len(data)

            print(f"{len(addresses)-data_len} tokens not in response")

            for i,token_data in enumerate(data):
                address = AddressHash(token_data["address"])

                decimals = token_data["decimals"]
                total_supply = token_data["total_supply"]/(10**decimals)
                id = TokenMeta(
                    id=bigint(0),
                    name=token_data["name"],
                    symbol=token_data["symbol"],
                    decimals=decimals,
                    created_time=token_data["block_time"],
                ).insert_or_update(chain=chain,token_address=address)

                TokenStats(
                    id=id,
                    total_supply=total_supply
                )._upsert_by_id(
                    dont_update=["circulating","price_change","holders","liquidity"],
                    db=db
                )

                print(f"{i+1}/{data_len} Token Inserted")