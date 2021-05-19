from core.Holders import Holders
from time import time
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry
from library.requests import get
import re

from core.sources.BaseSource import BaseSource

class BscScan(BaseSource):
    url = "https://bscscan.com/"

    limit_calls = 3
    limit_period = 6

    def __init__(self, apikey) -> None:
        self.apikey = apikey

    def address_token_res(self,address):
        return self.request(f"/token/{address}#readContract")

    def address_res(self,address):
        return self.request(f"/address/{address}")

    def get(self,address):
        res = self.address_token_res(address)
        soup = BeautifulSoup(res.text,"html.parser")
        token_type = soup.select(
            "#ContentPlaceHolder1_divSummary .card-header-title [data-original-title]"
        )[0].get_text()
        if token_type != "BEP-20":
            return [None,None]
        
        args = {}

        # Total Supply
        total_supply = soup.select(
            "#ContentPlaceHolder1_tr_valuepertoken + div > div:nth-child(2)"
        )[0].get_text().strip().split(" ")[0]
        args["total_supply"] = float(total_supply.replace(",",""))
        
        holders_count = int(soup.select(
            "#ContentPlaceHolder1_tr_tokenHolders > div:nth-child(2) > div:last-child"
        )[0].get_text().replace(" addresses","").replace(",",""))

        args["holders"] = holders_count

        # Decimals
        args["decimals"] = int(soup.select(
            "#ContentPlaceHolder1_trDecimals > div:first-child > div:nth-child(2)"
        )[0].get_text())

        args["description"] = ""
        args["bscscan_img"] = ""
        try:
            schema = self.parse_soup_json(soup,"script[type='application/ld+json']")
            args["description"] = schema.get("description","")
            args["bscscan_img"] = schema.get("image","")
            trimstart = "https://BscScan.com/token/images/"
            if args["bscscan_img"][:len(trimstart)] != trimstart:
                raise Exception(f"Img Url is not formatted correctly: {args['bscscan_img']}")
            args["bscscan_img"] = args["bscscan_img"][len(trimstart):]

        except Exception as e:
            print(e)
        
        args["source_verified"] = self.get_source(address) is not None

        holders = [] if holders_count == 0 else self.get_holders(soup, address)
        
        return args,holders
    
    @sleep_and_retry
    @limits(calls=4,period=1)
    def api_call(self,module,action,**parameters):
        params = [
            f"{key}={value}"
            for key,value
            in parameters.items()
        ]
        param_string = "" if len(params) < 1 else "&" + ('&'.join(params))
        query_string = f"?module={module}&action={action}&apikey={self.apikey}{param_string}"
        url = f"https://api.bscscan.com/api{query_string}"
        return (get(url)).json()

    def get_source(self,address):
        data = self.api_call("contract","getsourcecode",address=address)
        if data["status"] == "0":
            raise Exception(data["result"])
        
        source = data["result"][0]["SourceCode"]
        return None if source == "" else source

    @staticmethod
    def parse_sid(soup):
        pattern = '(?<=var sid = \')([\s\S][^\']+)'
        script_tag = soup.select('body > script[type="text/javascript"]')[0]
        return re.search(pattern,script_tag.string).group(0)

    def get_holders(self,previous_soup,address):
        sid = self.parse_sid(previous_soup)
        total_supply = 1000000
        res = self.request(f"/token/generic-tokenholders2?m=normal&a={address}&s={total_supply}&sid={sid}&p=1")

        holders = []

        soup = BeautifulSoup(res.text,"html.parser")
        for row in soup.select("table > tbody > tr"):
            cols = row.select("td")
            if len(cols) < 5:
                print("No Holders")
                return []
            rank_col,address_col,quantity_col,perc_col,analytics_cols = cols
            holder_args = dict(
                contract=address,
                holder=None,
                holder_tag="",
                holding=None,
                updated_time=time(),
                source="bscscan"
            )
            span = address_col.select("span")[0]
            if "data-original-title" in span.attrs:
                holder_args["holder_tag"] = span.get_text()
            
            holder_args["holder"] = span.select("a")[0].attrs["href"].split("?a=")[-1]

            holder_args["holding"] = float(quantity_col.get_text().replace(",",""))
            if holder_args["holding"] == 0:
                print("Wait, what?")
                print(row)

            holder = Holders(**holder_args)
            holders.append(holder)

        return holders