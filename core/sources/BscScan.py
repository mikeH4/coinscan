from typing import Optional
from core.types.db_types import ChainEnum, bigint, numeric
from library.RequestManager.CentralProxy import CentralProxy
from core.Wallets.WalletMeta import WalletMeta
from core.Wallets.WalletHoldings import WalletHoldings
from time import sleep
from core.types.AddressHash import AddressHash
from library.BaseSource import BaseSource
from bs4 import BeautifulSoup

class BscScan(BaseSource):
    url = "https://bscscan.com/"

    request_manager = CentralProxy

    def holders(self, address: AddressHash) -> Optional[tuple[int,list[tuple[AddressHash,WalletMeta,WalletHoldings]]]]:
        try:
            res = self.request("/token/generic-tokenholders2",params=dict(
                a=str(address)
            ))
            if res.status_code == 500:
                raise Exception(f"Internal Server Error with {res.status_code}")

            soup = BeautifulSoup(res.text,"html.parser")

            try:
                total_holders = int((
                    soup.select("#maintable > div:nth-child(2) > p")[0]
                    .get_text() # type: ignore
                    .lower()
                    .split("a total of ")
                )[1].split(" ")[0].replace(",",""))
            except IndexError as e:
                maintain = soup.select("#maintable")
                print(maintain)
                raise Exception(f"Error parsing total holders: {address}")

            wallets: list[tuple[AddressHash,WalletMeta,WalletHoldings]] = []
            for row in soup.select("table > tbody > tr"):
                cols = row.select("td") # type: ignore
                if len(cols) < 5:
                    print("No Holders")
                    return (total_holders,[])
                if len(cols) == 5:
                    rank_col,address_col,quantity_col,perc_col,analytics_cols = cols
                elif len(cols) == 6:
                    rank_col,address_col,quantity_col,perc_col,value_col,analytics_cols = cols
                else:
                    raise Exception(f"Unknown number of cols {len(cols)}")

                wallet_holdings = WalletHoldings(
                    wallet_id=bigint(0),
                    token_id=bigint(0),
                    supply=numeric(0),
                    liquidity=numeric(0)
                )
                wallet_meta = WalletMeta(
                    id=bigint(0),
                    is_contract=False,
                    bscscan_tag=""
                )

                wallet = None

                span = address_col.select("span")[0]
                if "title" in span.attrs:
                    wallet_meta.bscscan_tag = span.get_text()

                wallet = span.select("a")[0].attrs["href"].split("?a=")[-1]
                if wallet.lower() == "0x000000000000000000000000000000000000dead":
                    wallet = "0x0000000000000000000000000000000000000000"

                wallet_holdings.supply = numeric(quantity_col.get_text().replace(",",""))
                if wallet_holdings.supply == 0:
                    print("Wait, what?")
                    print(row)
                    continue

                wallet_meta.is_contract = len(address_col.select("i[title='Contract']")) > 0

                wallets.append((AddressHash(wallet),wallet_meta,wallet_holdings))

            return (total_holders,wallets)
        except Exception as e:
            print(e)
            print(f"Error parsing holders from BscScan: {address}")
            return None
    
    def recently_verified(self):
        res = self.request("/contractsVerified")
        soup = BeautifulSoup(res.text,"html.parser")
        addresses = [
            tag.get_text() # type: ignore
            for tag
            in soup.select("#transfers [title='Verified Code'] + a")
        ]
        return addresses

    def address_info(self, address: AddressHash):
        try:
            res = self.request(f"/address/{address}")
            soup = BeautifulSoup(res.text,"html.parser")
            
            contract_or_address = soup.select("#icon")[0].parent.get_text().strip().split(" ")[0] # type: ignore
            is_contract = contract_or_address.lower() == "Contract"

            spans = soup.select("[title='Public Name Tag (viewable by anyone)']")
            bscscan_tag = ""
            if len(spans) > 0:
                bscscan_tag = spans[0].get_text() # type: ignore

            return dict(
                is_contract=is_contract,
                bscscan_tag=bscscan_tag
            )
        except Exception as e:
            print(e)
            print("Error parsing is_contract from BscScan:")
            sleep(3)
        
class EtherScan(BscScan):
    url = "https://etherscan.io/"

class ChainScan():
    def __new__(cls, chain: ChainEnum):
        if chain == "bsc":
            return BscScan()
        elif chain == "eth":
            return EtherScan()
        raise TypeError(f"{chain} is not a valid chain")