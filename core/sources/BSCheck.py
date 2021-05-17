from core.sources.BaseSource import BaseSource
from bs4 import BeautifulSoup
import re

from library.backoff import backoff

class BSCheck(BaseSource):
    url = "http://www.bscheck.eu/"
    
    limit_calls = 1
    limit_period = 2

    def _get_nonce(self) -> str:
        pattern = '(?<=var m = ")([\s\S][^"]+)'
        res = self.request("/")
        soup = BeautifulSoup(res.text,"html.parser")
        script_tag = soup.select("html > script")[0]
        return re.search(pattern,script_tag.string).group(0)
    
    def __init__ (self) -> None:
        self.nonce = backoff(self._get_nonce)

    def address_res(self, address):
        return self.request(f"/check_contract.php?contract={address}&sel=0&m={self.nonce}")

    def get(self, address) -> dict:
        res = self.address_res(address)
        return self.parse(res)
        
    def parse(self, res) -> dict:
        # Rating "" will tell us that it hasn't been scanned
        default_args = dict(
            rating="",
            honeypot_check = False,
            owner_renounced=False,
            dev_liquidity_check=False,
            lp_check=False,
            top_holders_check=False
        )

        text = res.text
        str_text = str(text)
        if (
            "BSCscan error" in str_text or
            "This token has less than 10 holders - Please retry later..." in str_text
        ):
            return default_args
        else:
            soup = BeautifulSoup(text,"html.parser")
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