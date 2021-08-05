from core.types.db_types import ChainEnum
from library.Repeater import Repeater
from core.sources.BscScan import ChainScan
from core.Token.TokenMeta import TokenMeta
from library.database.postgres import DB

def main():
    with DB() as db:
        repeater = Repeater(min=12, max=60*2)

        while repeater.loop():
            for chain in ChainEnum.enum_opts:
                chain = ChainEnum(chain)
                addresses = ChainScan(chain).recently_verified()
                addresses_len = len(addresses)

                for i,address in enumerate(addresses):
                    TokenMeta.update(
                        chain=chain,
                        token_address=address,
                        db=db,
                        source_verified=True
                    )
                    print(f"{i+1}/{addresses_len} {address} has been verifed")
                
                db.conn.commit()