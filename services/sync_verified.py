from core.types.db_types import ChainEnum
from core.sources.BscScanApi import ChainScanApi
from core.Token.TokenMeta import TokenMeta
from library.postgres import DB

def main():
    with DB() as db:
        for chain in ChainEnum.enum_opts:
            chain = ChainEnum(chain)
            addresses = TokenMeta.get_only_addresses(
                limit=None,
                where_cond=f"""
                WHERE token_meta.source_verified IS NOT TRUE
                AND address.chain = {chain}
                """
            )

            for i,address in enumerate(addresses):
                source_verified = (ChainScanApi(chain).source_code(
                    address=address
                ) is not None)
                TokenMeta.update(
                    chain=chain,
                    token_address=address,
                    db=db,
                    source_verified=source_verified
                )
                db.conn.commit()

                print(f"{i+1}/{len(addresses)} Source Updated: {address} => {str(source_verified)}")