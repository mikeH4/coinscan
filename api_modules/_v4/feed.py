from typing import Optional
from core.types.db_types import ChainEnum, bigint, numeric
from fastapi import APIRouter
from library.database.postgres import DB

from core.Token.ViewableToken import ViewableToken
from core.Token.ViewableTokenListings import ViewableTokenListings
from core.Token.Query import Query

router = APIRouter(
    prefix="/feed"
)

@router.get("/latest")
def latest(
    only_contract_verified: bool = False,
    min_liquidity_500: bool = False,
    chain: str = ChainEnum("bsc")
):
    chain_is: Optional[ChainEnum] = None if chain == "" else ChainEnum(chain)
    return Query.get_filtered(dict(
        only_source_verified=only_contract_verified,
        min_liquidity_500=min_liquidity_500,
        chain=chain_is
    ),limit=100)

@router.get("/listings")
def listings():
    with DB() as db:
        listings = ViewableTokenListings.new_listings()
        
        keyed_listings: dict[bigint,list[ViewableTokenListings]] = dict()
        for listing in listings:
            if listing.id not in keyed_listings: keyed_listings[listing.id] = []
            keyed_listings[listing.id].append(listing)

        keyed_tokens = ViewableToken.keyed_by_ids(ids=list(keyed_listings.keys()), db=db)
        sorted_tokens = []

        for id in list(keyed_listings.keys()):
            if id not in keyed_tokens: continue
            sorted_tokens.append(keyed_tokens[id])

        return dict(
            listings=keyed_listings,
            tokens=sorted_tokens
        )

@router.get("/rising")
def rising():
    with DB() as db:
        rows = db.get_all("""
        SELECT id, price_change FROM token_stats
        WHERE liquidity > 7
        ORDER BY price_change DESC
        LIMIT 100
        """)

        keyed_rising = {
            bigint(row[0]): numeric(row[1])
            for row
            in rows
        }

        keyed_tokens = ViewableToken.keyed_by_ids(ids=list(keyed_rising.keys()), db=db)
        sorted_tokens = []

        for id in list(keyed_rising.keys()):
            if id not in keyed_tokens: continue
            sorted_tokens.append(keyed_tokens[id])

        return dict(
            change=keyed_rising,
            tokens=sorted_tokens
        )
    
@router.get("/search/{search}")
def search(search: str):
    tokens = ViewableToken.search(keyword=search)
    return tokens