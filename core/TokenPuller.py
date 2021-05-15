from bs4 import BeautifulSoup
import json
from datetime import date, datetime
from ratelimit import limits, sleep_and_retry

from library.requests import get
from library.db import DB

from core.Token import Token
from core.Address import Address

class Request:
    @staticmethod
    def join(host,path):
        return host.rstrip("/") + "/" + path.lstrip("/")

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

    def get_existing_addresses(self,of=[],updated_after=None):
        of = list(map(str,of))
        placeholder = self.db.placeholder(len(of))
        sql = f"SELECT address FROM tokens WHERE address IN ({placeholder})"
        if updated_after is not None:
            sql += " AND updated > ?"
            of += [updated_after]
        addrs = [row[0] for row in self.db.get_all(sql,of)]
        return addrs

    @staticmethod
    def bscheck(address):
        res = Request.bscheck(f"/check_contract.php?contract={address}")
        
        # Rating "" will tell us that it hasn't been scanned
        default_args = dict(
            rating="",
            honeypot_check = False,
            owner_renounced=False,
            dev_liquidity_check=False,
            lp_check=False,
            top_holders_check=False
        )

        text = str(res.text)
        if (
            "BSCscan error" in text or
            "This token has less than 10 holders - Please retry later..." in text
        ):
            return default_args
        else:
            soup = BeautifulSoup(res.text,"html.parser")
            try:
                new_args = dict(
                    rating=soup.select("#report_group3 + div:last-child")[0].get_text().replace("SAFESCORE:","").lower(),
                    honeypot_check=soup.select("#report_honeypot > #report_tile_result")[0].get_text() == "Sell is OK",
                    owner_renounced=soup.select("#report_owner > #report_tile_result")[0].get_text() == "Owner renounced !",
                    dev_liquidity_check=soup.select("#report_dev > #report_tile_result")[0].get_text() == "Dev liquidity OK !",
                    lp_check=soup.select("#report_lp > #report_tile_result")[0].get_text() == "LP check OK !",
                    top_holders_check=soup.select("#report_holders > #report_tile_result")[0].get_text() == "Top holders liquidity OK"
                )
                return new_args
            except Exception as e:
                print(e)
                return default_args

    @staticmethod
    def tokensniffer(address):
        res = Request.tokensniffer(f"/token/{address}")
        if res.status_code == 500:
            # deployed 0 will tell us it hasn't been scanned
            return dict(
                deployed=0,
                first_seen=0,
                source_md5="",
                similar_count=0,
                similar_viewable=0,
                no_older_tokens=False,
                not_proxy=False,
                not_pausable=False
            )
        else:
            data = TokenPuller.parse_soup_json(
                BeautifulSoup(res.text,"html.parser"),
                "script#__NEXT_DATA__"
            )["props"]["pageProps"]
            token_data = data["token"]

            return dict(
                deployed=datetime.strptime(token_data["created_at"],"%Y-%m-%dT%H:%M:%S.%fZ").timestamp(),
                first_seen=int(token_data["timestamp_first_seen"])/1000,
                source_md5=token_data.get("source_md5",None) or "",
                similar_count=int(token_data["similarCount"]),
                similar_viewable=int(len(token_data["similar"])),
                no_older_tokens=token_data["hasOlderTokens"] == False,
                not_pausable=data["auditReport"].get("testForPausable",True) == False,
                not_proxy=data["auditReport"].get("testForProxy",True) == False,
            )


    def __init__(self, ignore_existing = "recent") -> None:
        self.db = DB("data/tokens.db")

        res = Request.tokenfomo()
        data = self.parse_soup_json(
            BeautifulSoup(res.text,"html.parser"),
            "script#__NEXT_DATA__"
        )["props"]["pageProps"]["tokens"]

        existing_addrs = [] if not ignore_existing else self.get_existing_addresses(
            [row["addr"] for row in data],
            # In last 30 min
            updated_after=(
                int(datetime.now().timestamp()-(60*60*2))
                if ignore_existing == "recent"
                else None
            )
        )

        for record in data:
            if record["chainId"] != "BSC":
                continue
            if record["addr"] in existing_addrs:
                print("Skipped:",record["addr"])
                continue

            address = Address(record["addr"])
            init_args = dict(
                name=record["name"],
                symbol=record["symbol"],
                address=address,
                block_time=int(record["blockTime"]),
                updated=int(datetime.now().timestamp())
            )
            res = Request.bscscan(f"/token/{address}#readContract")
            soup = BeautifulSoup(res.text,"html.parser")
            
            token_type = soup.select(
                "#ContentPlaceHolder1_divSummary .card-header-title [data-original-title]"
            )[0].get_text()
            if token_type != "BEP-20":
                continue
            
            # Total Supply
            total_supply = soup.select(
                "#ContentPlaceHolder1_tr_valuepertoken + div > div:nth-child(2)"
            )[0].get_text().strip().split(" ")[0]
            init_args["total_supply"] = float(total_supply.replace(",",""))
            
            # Decimals
            init_args["decimals"] = int(soup.select(
                "#ContentPlaceHolder1_trDecimals > div:first-child > div:nth-child(2)"
            )[0].get_text())

            res = Request.bscscan(f"/address/{address}")
            soup = BeautifulSoup(res.text,"html.parser")

            init_args["source_verified"] = bool(soup.select("#ContentPlaceHolder1_contractCodeDiv"))

            # BscCheck
            init_args.update(self.bscheck(address))
            
            # Token Sniffer
            init_args.update(self.tokensniffer(address))
            
            Token(**init_args).insert_or_update(db=self.db)
            self.db.conn.commit()

        self.db.close()