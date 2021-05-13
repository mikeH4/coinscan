from os import stat
from bs4 import BeautifulSoup
import json
from datetime import datetime
from ratelimit import limits, sleep_and_retry

from library.requests import get
from library.db import DB

from core.Token import Token
from core.Address import Address

class Request:
    @staticmethod
    def join(host,path):
        return host.rtrim("/") + "/" + path.ltrim("/")

    @staticmethod
    @sleep_and_retry
    @limits(calls=1, period=10)
    def tokenfomo(path = "/"):
        return get(Request.join("https://tokenfomo.io/",path))

    @staticmethod
    @sleep_and_retry
    @limits(calls=2, period=2)
    def bscscan(path = "/"):
        return get(Request.join("https://bscscan.com/",path))

    @staticmethod
    @sleep_and_retry
    @limits(calls=2, period=3)
    def tokensniffer(path = "/"):
        return get(Request.join("https://tokensniffer.com/",path))

    @staticmethod
    @sleep_and_retry
    @limits(calls=1, period=2)
    def bscheck(path = "/"):
        return get(Request.join("http://www.bscheck.eu/",path))


class TokenPuller:
    @staticmethod
    def parse_soup_json(soup,selector):
        script_content = soup.select(selector)[0].string
        return json.loads(script_content)

    def __init__(self, address) -> None:
        self.db = DB("data/tokens.db")

        res = Request.tokenfomo()
        data = self.parse_soup_json(
            BeautifulSoup(res.text),
            "script#__NEXT_DATA__"
        )["props"]["pageProps"]["tokens"]

        for record in data:
            if record["chainId"] != "BSC":
                continue
            address = Address(record["addr"])
            init_args = dict(
                name=record["name"],
                symbol=record["symbol"],
                address=address,
                block_time=int(record["blockTime"])
            )
            res = Request.bscscan(f"/token/{address}#readContract")
            soup = BeautifulSoup(res.text)
            
            # Total Supply
            total_supply = soup.select(
                "#ContentPlaceHolder1_tr_valuepertoken + div > div:nth-child(2) > span:first-child"
            )[0].get_text()
            init_args["total_supply"] = int(total_supply.replace(",",""))
            
            # Decimals
            init_args["decimals"] = int(soup.select(
                "#ContentPlaceHolder1_trDecimals > div:first-child > div:nth-child(2)"
            )[0].get_text())

            res = Request.bscscan(f"/address/{address}")
            soup = BeautifulSoup(res.text)

            init_args["source_verified"] = bool(soup.select("#ContentPlaceHolder1_contractCodeDiv"))

            # BscCheck

            res = Request.bscheck(f"/check_contract.php?contract={address}")
            if str(res.text) == "BSCscan error":
                # Rating "" will tell us that it hasn't been scanned
                init_args["rating"] = ""
                init_args["honeypot_check"] = False
                init_args["owner_renounced"] = False
                init_args["dev_liquidity_check"] = False
                init_args["lp_check"] = False
                init_args["top_holders_check"] = False
            else:
                soup = BeautifulSoup(res.text)
                init_args["rating"] = soup.select("body > div:last-child")[0].get_text().replace("SAFESCORE:")
                init_args["honeypot_check"] = soup.select("#report_honeypot > #report_tile_result")[0].get_text() == "Sell is OK"
                init_args["owner_renounced"] = soup.select("#report_owner > #report_tile_result")[0].get_text() == "Owner renounced !"
                init_args["dev_liquidity_check"] = soup.select("#report_dev > #report_tile_result")[0].get_text() == "Dev liquidity OK !"
                init_args["lp_check"] = soup.select("#report_lp > #report_tile_result")[0].get_text() == "LP check OK !"
                init_args["top_holders_check"] = soup.select("#report_holders > #report_tile_result")[0].get_text() == "Top holders liquidity OK"

            
            # Token Sniffer
            res = Request.tokensniffer(f"/token/{address}")
            if res.status_code == 500:
                # deployed 0 will tell us it hasn't been scanned
                init_args["deployed"] = 0
                init_args["first_seen"] = 0
                init_args["source_md5"] = ""
                init_args["similar_count"] = 0
                init_args["similar_viewable"] = 0
                init_args["no_older_tokens"] = False
                init_args["not_proxy"] = False
                init_args["not_pausable"] = False
            else:
                data = self.parse_soup_json(
                    BeautifulSoup(res.text),
                    "script#__NEXT_DATA__"
                )["props"]["pageProps"]
                token_data = data["data"]

                init_args["deployed"] = datetime.strptime(token_data["created_at"],"%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                init_args["first_seen"] = int(token_data["timestamp_first_seen"])/1000
                init_args["source_md5"] = token_data.get("source_md5",None) or ""
                init_args["similar_count"] = int(token_data["similarCount"])
                init_args["similar_viewable"] = int(len(token_data["similar"]))
                init_args["no_older_tokens"] = token_data["hasOlderTokens"] == False
                init_args["not_pausable"] = data["auditReport"]["testForPausable"] == False
                init_args["not_proxy"] = data["auditReport"]["testForProxy"] == False

            Token(init_args).insert_or_update(db=self.db)

        self.db.close()