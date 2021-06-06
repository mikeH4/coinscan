from library.postgres import DB
from library.BaseModel import BaseModel

from core.Token.Token import Token
from core.Token.TokenMeta import TokenMeta
from core.Token.BSCheckRating import BSCheckRating
from core.Token.TokenSnifferRating import TokenSnifferRating

with DB("tokens") as db:
    # Check to ensure script has not been run already
    try:
        db.get("SELECT * FROM migrator5_tokens LIMIT 1")
        print("Table exists: Exiting")
        exit(0)
    except Exception as e:
        db.rollback()

    query = db.query("""
    ALTER TABLE tokens RENAME TO migrator5_tokens
    """)
    db.conn.commit()

    for _class in [Token,TokenMeta,BSCheckRating,TokenSnifferRating]:
        print(_class)
        db.query(_class._db_create())
    
    db.conn.commit()

    query = db.query("""
    INSERT INTO bscheck_rating
    (address,rating,honeypot_check,owner_renounced,dev_liquidity_check,lp_check,top_holders_check,updated)
    SELECT
    address,rating,honeypot_check,owner_renounced,dev_liquidity_check,lp_check,top_holders_check,updated
    FROM migrator5_tokens
    WHERE rating != ''
    """)
    query = db.query("""
    INSERT INTO tokensniffer_rating
    (address,deployed,first_seen,source_md5,similar_count,similar_viewable,no_older_tokens,not_proxy,not_pausable,updated)
    SELECT
    address,deployed,first_seen,source_md5,similar_count,similar_viewable,no_older_tokens,not_proxy,not_pausable,updated
    FROM migrator5_tokens
    WHERE deployed != 0
    """)
    query = db.query("""
    INSERT INTO token_meta
    (address,decimals,total_supply,source_verified,holders,block_time)
    SELECT
    address,decimals,total_supply,source_verified,holders,block_time
    FROM migrator5_tokens
    """)
    query = db.query("""
    INSERT INTO tokens
    (address,name,symbol)
    SELECT
    address,name,symbol
    FROM migrator5_tokens
    """)
    db.conn.commit()