from core.Pair.TokenPair import TokenPair
from core.Wallets.WalletMeta import WalletMeta
from core.Wallets.WalletHoldings import WalletHoldings
from core.Token.TokenListings import TokenListings
from core.Token.TokenStats import TokenStats
from core.types.AddressHash import AddressHash
from core.types.db_types import ChainEnum, PlatformsEnum, bigint, numeric
from library.postgres import DB, PostgresDBException
from core.Token.TokenMeta import TokenMeta

stops = 10000

def import_tokens(*, old_db: DB, new_db: DB):
    count = int(old_db.get_all("SELECT COUNT(*) FROM token_meta")[0][0])
    for offset in range(0,count,stops):
        rows = old_db.get_all(
            f"""
            SELECT tokens.*, token_meta.*, token_prices.* FROM tokens
            LEFT JOIN token_meta ON tokens.address = token_meta.address
            LEFT JOIN token_prices ON tokens.address = token_prices.token
            LIMIT {stops} OFFSET {offset}
            """
        )
        for row in rows:
            (
                address, name, symbol,
                _, 
                decimals, total_supply, source_verified, holders,
                _, _, _,
                block_time,
                _,
                price_change, circulating, liquidity
            ) = row

            id = TokenMeta(
                id=bigint(0),
                name=name,
                symbol=symbol,
                decimals=decimals or -1,
                created_time=block_time or 0,
                source_verified=source_verified
            ).insert_or_update(
                chain=ChainEnum("bsc"),
                token_address=AddressHash(address),
                db=new_db
            )
            TokenStats(
                id=id,
                holders=holders,
                total_supply=total_supply,
                price_change=price_change,
                circulating=circulating,
                liquidity=liquidity
            )._upsert_by_id(db=new_db)
        
        print(f"Committed {offset}-{min(offset+stops,count)}")
        new_db.conn.commit()

def import_listings(*, old_db: DB, new_db: DB):
    count = int(old_db.get_all("SELECT COUNT(*) FROM listings")[0][0])
    for offset in range(0,count,stops):
        rows = old_db.get_all(
            f"""
            SELECT * FROM listings
            LIMIT {stops} OFFSET {offset}
            """
        )
        for row in rows:
            (
                token, platform, local_id,
                local_slug, added, updated
            ) = row
            
            id = TokenListings(
                id=bigint(0),
                platform=PlatformsEnum(platform),
                local_id=local_id,
                local_slug=local_slug,
                added=added,
            ).insert_or_update(
                chain=ChainEnum("bsc"),
                token_address=token,
                db=new_db
            )
        
        print(f"Committed {offset}-{min(offset+stops,count)}")
        new_db.conn.commit()

def import_wallet_meta(*, old_db: DB, new_db: DB):
    count = int(old_db.get_all("SELECT COUNT(*) FROM address_info")[0][0])
    for offset in range(0,count,stops):
        rows = old_db.get_all(
            f"""
            SELECT * FROM address_info
            LIMIT {stops} OFFSET {offset}
            """
        )
        nully = 0
        for row in rows:
            (
                address, is_contract, bscscan_tag,
                _, _
            ) = row
            try:
                id = WalletMeta(
                    id=bigint(0),
                    is_contract=is_contract,
                    bscscan_tag=bscscan_tag
                ).insert_or_update(
                    chain=ChainEnum("bsc"),
                    wallet_address=address,
                    db=new_db
                )
            except PostgresDBException as e:
                exists = e.pgcode == "23502"
                if exists:
                    nully += 1
                    new_db.rollback()
        
        print(f"Committed {offset}-{min(offset+stops,count)}")
        print("Null Type:",nully)
        new_db.conn.commit()

def import_wallet_holdings(*, old_db: DB, new_db: DB):
    count = int(old_db.get_all("SELECT COUNT(*) FROM holders")[0][0])
    for offset in range(0,count,stops):
        rows = old_db.get_all(
            f"""
            SELECT
                CASE WHEN holders.token IS NOT NULL
                    THEN holders.token ELSE pair_holders.token
                END AS token,
                CASE WHEN holders.wallet IS NOT NULL
                    THEN holders.wallet ELSE pair_holders.wallet
                END AS wallet,
                holders.supply,
                pair_holders.liquidity
            FROM (
                SELECT
                    contract AS token,
                    holder AS wallet,
                    holding AS supply
                FROM holders
                ORDER BY holders.contract ASC
                LIMIT {stops} OFFSET {offset}
            ) AS holders
            FULL OUTER JOIN (
                SELECT
                    pairs.token AS token,
                    holders.holder AS wallet,
                    holders.holding AS liquidity
                FROM holders
                JOIN pairs ON pairs.pair = holders.contract
                ORDER BY holders.contract ASC
                LIMIT {stops} OFFSET {offset}
            ) AS pair_holders ON
                pair_holders.token = holders.token AND
                pair_holders.wallet = holders.wallet
            """
        )
        for row in rows:
            token, wallet, supply, liquidity = row

            wallet_id, token_id = WalletHoldings(
                wallet_id=bigint(0),
                token_id=bigint(0),
                supply=numeric(supply or 0),
                liquidity=numeric(liquidity or 0)
            ).insert_full_upsert(
                chain=ChainEnum("bsc"),
                wallet_address=wallet,
                token_address=token,
                db=new_db
            )
        
        print(f"Committed {offset}-{min(offset+stops,count)}")
        new_db.conn.commit()

def import_pairs(*, old_db: DB, new_db: DB):
    count = int(old_db.get_all("SELECT COUNT(*) FROM pairs")[0][0])
    for offset in range(0,count,stops):
        rows = old_db.get_all(
            f"""
            SELECT * FROM pairs
            LIMIT {stops} OFFSET {offset}
            """
        )
        for row in rows:
            token, pair, _ = row
            
            TokenPair.insert_or_ignore(
                chain=ChainEnum("bsc"),
                token_address=token,
                pair_address=pair,
                db=new_db
            )
        
        print(f"Committed {offset}-{min(offset+stops,count)}")
        new_db.conn.commit()

with DB(auto_commit=False) as blockchain:
    with DB("tokens") as tokens_db:
        print("import_tokens")
        import_tokens(old_db=tokens_db,new_db=blockchain)
        print("import_listings")
        import_listings(old_db=tokens_db,new_db=blockchain)
        print("import_wallet_meta")
        import_wallet_meta(old_db=tokens_db,new_db=blockchain)
        print("import_wallet_holdings")
        import_wallet_holdings(old_db=tokens_db,new_db=blockchain)
        print("import_pairs")
        import_pairs(old_db=tokens_db,new_db=blockchain)