from core.Holders.Holders import Holders
from time import time
from core.types.Address import Address
from library.BaseSource import BaseSource
from bs4 import BeautifulSoup

class BscScan(BaseSource):
    url = "https://bscscan.com/"

    limit_calls = 1
    limit_period = 4

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
                        holder_tag="",
                        holding=None,
                        updated_time=time(),
                        source="bscscan"
                    )
                    span = address_col.select("span")[0]
                    if "title" in span.attrs:
                        holder_args["holder_tag"] = span.get_text()

                    holder_args["holder"] = span.select("a")[0].attrs["href"].split("?a=")[-1]
                    if holder_args["holder"].lower() == "0x000000000000000000000000000000000000dead":
                        holder_args["holder"] = "0x0000000000000000000000000000000000000000"
                        holder_args["holder_tag"] = "Dead"

                    holder_args["holding"] = float(quantity_col.get_text().replace(",",""))
                    if holder_args["holding"] == 0:
                        print("Wait, what?")
                        print(row)
                        continue

                    holder = Holders(**holder_args)
                    holders.append(holder)

                return (total_holders,holders)
            
            except Exception as e:
                print("Error parsing holders from BscScan:")
                print(soup)