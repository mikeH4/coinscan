from modules.db import CreateSQLTables

a = CreateSQLTables("data/db.db")

a += """
CREATE TABLE posts (
    id PRIMARY KEY NOT NULL ,
    title TEXT NOT NULL ,
    name TEXT NOT NULL ,
    created_utc INTEGER NOT NULL ,
    selftext TEXT NOT NULL ,
    selftext_html TEXT NOT NULL ,
    num_comments INTEGER NOT NULL,
    over_18 TEXT NOT NULL ,
    score INTEGER NOT NULL ,
    upvote_ratio FLOAT NOT NULL ,
    is_original_content TEXT NOT NULL ,
    is_self TEXT NOT NULL 
)
"""

a += """
CREATE TABLE latest (
    address TEXT PRIMARY KEY NOT NULL ,
    name TEXT NOT NULL ,
    symbol TEXT NOT NULL ,
    chain TEXT NOT NULL ,
    defunct INTEGER NOT NULL ,
    source_md5 STRING NOT NULL ,
    added INTEGER NOT NULL
)
"""
a += """
CREATE TABLE bscheck (
    address TEXT PRIMARY KEY NOT NULL ,
    rating TEXT NOT NULL ,
    burned_tokens INTEGER NOT NULL,
    total_supply INTEGER NOT NULL,
    holders INTEGER NOT NULL,
)
"""
a += """
CREATE TABLE top_holders (
    address TEXT PRIMARY KEY NOT NULL ,
    is_dev INTEGER NOT NULL,
    percentage FLOAT NOT NULL,
)
"""
a += """
CREATE TABLE tokensniffer (
    address TEXT PRIMARY KEY NOT NULL ,
    verified_source INTEGER NOT NULL ,
    prior_similar INTEGER NOT NULL ,
    proxy_contains INTEGER NOT NULL ,
    pausable_contains INTEGER NOT NULL ,
    defunct INTEGER NOT NULL ,
    source_md5 STRING NOT NULL ,
    deployed INTEGER NOT NULL
)
"""

a.execute()