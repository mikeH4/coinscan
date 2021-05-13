from modules.db import CreateSQLTables

a = CreateSQLTables("data/db.db")

a += """
CREATE TABLE tokens (
    name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    address VARCHAR(42) NOT NULL,
    block_time INTEGER NOT NULL,

    total_supply INTEGER NOT NULL,
    decimals INTEGER NOT NULL,
    source_verified BOOLEAN NOT NULL,

    rating TEXT NOT NULL,
    honeypot_check BOOLEAN NOT NULL,
    owner_renounced BOOLEAN NOT NULL,
    dev_liquidity_check BOOLEAN NOT NULL,
    lp_check BOOLEAN NOT NULL,
    top_holders_check BOOLEAN NOT NULL,

    deployed INTEGER NOT NULL,
    first_seen INTEGER NOT NULL,
    source_md5 TEXT NOT NULL,
    similar_count INTEGER NOT NULL,
    similar_viewable INTEGER NOT NULL,
    no_older_tokens BOOLEAN NOT NULL,
    not_proxy BOOLEAN NOT NULL,
    not_pausable BOOLEAN NOT NULL,
)
"""