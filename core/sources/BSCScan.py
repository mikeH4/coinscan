from core.sources.BaseSource import BaseSource
from bs4 import BeautifulSoup

class BscScan(BaseSource):
    url = "https://bscscan.com/"

    limit_calls = 3
    limit_period = 6

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
            return None
        
        args = {}

        # Total Supply
        total_supply = soup.select(
            "#ContentPlaceHolder1_tr_valuepertoken + div > div:nth-child(2)"
        )[0].get_text().strip().split(" ")[0]
        args["total_supply"] = float(total_supply.replace(",",""))
        
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

        res = self.address_res(address)
        soup = BeautifulSoup(res.text,"html.parser")

        args["source_verified"] = bool(soup.select("#ContentPlaceHolder1_contractCodeDiv"))
        
        return args