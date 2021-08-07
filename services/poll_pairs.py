from library.database.postgres import DB
from library.Repeater import Repeater
from core.sources.ScannerApi import ScannerApi
from core.Pair.TokenPair import TokenPair
from core.types.AddressHash import AddressHash
from core.types.db_types import ChainEnum
from core.Pair.TokenPair import TokenPair

def main():
    with DB() as db:
        repeater = Repeater(min=60*5)

        limit = 200

        # 2.5 min max
        while repeater.loop():
            for chain in ChainEnum.enum_opts:
                chain = ChainEnum(chain)
                existing_pairs = TokenPair.count(chain=chain,db=db)
                all_pairs = ScannerApi().token_pairs_count(chain)
                
                print(f"All Pairs: {all_pairs}")
                print(f"Existing Pair: {existing_pairs}")
                print(f"Pairs to add: {all_pairs - existing_pairs}")

                for offset in range(existing_pairs, all_pairs, limit):
                    print(f"From: {offset}")
                    data = ScannerApi().token_pairs(chain,limit=limit,offset=offset)

                    for i,token_pair in enumerate(data):
                        token, pair = (AddressHash(token_pair[0]), AddressHash(token_pair[1]))

                        TokenPair.insert_or_ignore(
                            chain=chain,
                            token_address=token,
                            pair_address=pair
                        )

                        print(f"{i+1}/{len(data)} Pair Inserted/Ignored: {pair}")
                    
                    db.conn.commit()