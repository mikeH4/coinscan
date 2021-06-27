from core.Holders.AddressInfo import AddressInfo
from core.Holders.Holders import Holders
from time import sleep, time
from core.types.Address import Address, BlockOrTransactionHash
from library.BaseSource import BaseSource
from bs4 import BeautifulSoup

class BscScan(BaseSource):
    url = "https://bscscan.com/"

    limit_calls = 1
    limit_period = 2

    def holders(self,address:Address):
        while True:
            try:
                res = self.request("/token/generic-tokenholders2",params=dict(
                    a=str(address)
                ))

                soup = BeautifulSoup(res.text,"html.parser")

                try:
                    total_holders = int((
                        soup.select("#maintable > div:nth-child(2) > p")[0]
                        .get_text()
                        .lower()
                        .split("a total of ")
                    )[1].split(" ")[0].replace(",",""))
                except IndexError as e:
                    print("Error getting total holders:")
                    raise Exception("Error parsing total holders")

                holders = []
                for row in soup.select("table > tbody > tr"):
                    cols = row.select("td")
                    if len(cols) < 5:
                        print("No Holders")
                        return [total_holders,[]]
                    if len(cols) == 5:
                        rank_col,address_col,quantity_col,perc_col,analytics_cols = cols
                    elif len(cols) == 6:
                        rank_col,address_col,quantity_col,perc_col,value_col,analytics_cols = cols
                    
                    holder_args = dict(
                        contract=address,
                        holder=None,
                        holding=None,
                        updated_time=time(),
                        source="bscscan"
                    )
                    bscscan_tag = ""

                    span = address_col.select("span")[0]
                    if "title" in span.attrs:
                        bscscan_tag = span.get_text()

                    holder_args["holder"] = span.select("a")[0].attrs["href"].split("?a=")[-1]
                    if holder_args["holder"].lower() == "0x000000000000000000000000000000000000dead":
                        holder_args["holder"] = "0x0000000000000000000000000000000000000000"

                    holder_args["holding"] = float(quantity_col.get_text().replace(",",""))
                    if holder_args["holding"] == 0:
                        print("Wait, what?")
                        print(row)
                        continue

                    is_contract = len(address_col.select("i[title='Contract']")) > 0
                    
                    holder = Holders(**holder_args)
                    address_info = AddressInfo(
                        address=Address(holder.holder),
                        is_contract=is_contract,
                        bscscan_tag=bscscan_tag,
                        updated=time(),
                        added=time(),
                    )

                    holders.append((holder,address_info))

                return (total_holders,holders)
            
            except Exception as e:
                print("Error parsing holders from BscScan:")
                sleep(3)
    
    def recently_verified(self):
        res = self.request("/contractsVerified")
        soup = BeautifulSoup(res.text,"html.parser")
        addresses = [
            tag.get_text()
            for tag
            in soup.select("#transfers [title='Verified Code'] + a")
        ]
        return addresses

    def creation(self,address:Address):
        try:
            res = self.request(f"/address/{address}")
            soup = BeautifulSoup(res.text,"html.parser")
            creator_address, creation_tx = soup.select(
                "#ContentPlaceHolder1_trContract > div > div:nth-child(2)"
            )[0].get_text().split(" at txn ")
            creator = Address(creator_address.strip())
            creation_tx = BlockOrTransactionHash(creation_tx.strip())
            return (creator,creation_tx)
        except Exception as e:
            print("Error parsing creator from BscScan:")
            sleep(3)
    
    def address_info(self,address:Address):
        try:
            res = self.request(f"/address/{address}")
            soup = BeautifulSoup(res.text,"html.parser")
            
            contract_or_address = soup.select("#icon")[0].parent.get_text().strip().split(" ")[0]
            is_contract = contract_or_address.lower() == "Contract"

            spans = soup.select("[title='Public Name Tag (viewable by anyone)']")
            bscscan_tag = ""
            if len(spans) > 0:
                bscscan_tag = spans[0].get_text()

            return dict(
                is_contract=is_contract,
                bscscan_tag=bscscan_tag
            )
        except Exception as e:
            print(e)
            print("Error parsing is_contract from BscScan:")
            sleep(3)