from core.Wallets.ViewableWalletMeta import ViewableWalletMeta
from core.Wallets.ViewableWalletHoldings import TokenOrWallet, ViewableWalletHoldings
from fastapi import APIRouter, HTTPException

from core.types.AddressHash import AddressHash
from core.types.db_types import ChainEnum

router = APIRouter(
    prefix="/wallet"
)

@router.get("/{chain}/{wallet_address}")
def wallet(chain: ChainEnum, wallet_address: AddressHash):
    wallet = ViewableWalletMeta.get(chain, wallet_address)
    if wallet is None: raise HTTPException(404)

    return wallet

@router.get("/{chain}/{wallet_address}/tokens")
def wallet_tokens(chain: ChainEnum, wallet_address: AddressHash):
    return ViewableWalletHoldings._get_holdings(chain, wallet_address, TokenOrWallet("wallet") )