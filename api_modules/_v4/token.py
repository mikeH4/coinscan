from fastapi import APIRouter,HTTPException

from core.types.db_types import ChainEnum
from core.types.AddressHash import AddressHash

from core.Wallets.ViewableWalletHoldings import TokenOrWallet, ViewableWalletHoldings
from core.Token.ViewableToken import ViewableToken
from core.Token.ViewableTokenListings import ViewableTokenListings

router = APIRouter(
    prefix="/token"
)

@router.get("/{chain}/{token_address}")
def token(chain: ChainEnum, token_address: AddressHash):
    token = ViewableToken.get(chain, token_address)
    if token is None: raise HTTPException(404)
    return token

@router.get("/{chain}/{token_address}/wallets")
def wallets(chain: ChainEnum, token_address: AddressHash):
    return ViewableWalletHoldings._get_holdings(chain, token_address, TokenOrWallet("token"), limit=15)

@router.get("/{chain}/{token_address}/listings")
def listings(chain: ChainEnum, token_address: AddressHash):
    return ViewableTokenListings.for_token(chain, token_address)