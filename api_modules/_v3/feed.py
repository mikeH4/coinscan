from fastapi import APIRouter
from library.postgres import DB

from core.Token.ViewableToken import ViewableToken
from core.misc.ViewableListings import ViewableListings
from core.misc.TokenPrices import TokenPrices
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
    with DB("tokens") as db:
        listings = ViewableListings.new_listings(db=db)
        listing_keys = list(listings.keys())
        tokens = ViewableToken.get_addresses(
            listing_keys,
            db=db
        )
        sorted_tokens = []
        for address in listing_keys:
            if address not in tokens:
                del listings[address]
                continue
            sorted_tokens.append(tokens[address])
        return dict(
            listings=listings,
            tokens=sorted_tokens
        )

@router.get("/rising")
def rising():
    with DB("tokens") as db:
        rising = TokenPrices.rising(db=db)
        rising_keys = list(rising.keys())
        tokens = ViewableToken.get_addresses(
            rising_keys,
            db=db
        )
        sorted_tokens = []
        for address in rising_keys:
            if address not in tokens:
                del rising[address]
                continue
            sorted_tokens.append(tokens[address])
        return dict(
            change=rising,
            tokens=sorted_tokens
        )
    
@router.get("/search/{search}")
def search(search: str):
    tokens = ViewableToken.search(search)
    return tokens