from core.types.db_types import bigint, numeric
from fastapi import APIRouter
from library.postgres import DB

from core.Token.ViewableToken import ViewableToken
from core.Token.ViewableTokenListings import ViewableTokenListings
from core.Token.Query import Query

router = APIRouter(
    prefix="/feed"
)

@router.get("/latest")
def latest(
    only_contract_verified: bool = False,
    min_liquidity_500: bool = False
):
    return Query.get_filtered(dict(
        only_source_verified=only_contract_verified,
        min_liquidity_500=min_liquidity_500
    ),limit=100)

@router.get("/listings")
def listings():
    with DB() as db:
        listings = ViewableTokenListings.new_listings()
        
        keyed_listings: dict[bigint,ViewableTokenListings] = dict()
        for listing in listings: keyed_listings[listing.id] = listing

        tokens = ViewableToken.keyed_by_ids(ids=list(keyed_listings.keys()), db=db)

        return dict(
            listings=keyed_listings,
            tokens=tokens
        )

@router.get("/rising")
def rising():
    with DB() as db:
        rows = db.get_all("""
        SELECT id, price_change FROM token_stats
        WHERE liquidity > 7
        ORDER BY price_change DESC
        """)

        keyed_rising = {
            bigint(row[0]): numeric(row[1])
            for row
            in rows
        }

        tokens = ViewableToken.keyed_by_ids(ids=list(keyed_rising.keys()), db=db)

        return dict(
            change=rising,
            tokens=tokens
        )
    
@router.get("/search/{search}")
def search(search: str):
    tokens = ViewableToken.search(search)
    return tokens