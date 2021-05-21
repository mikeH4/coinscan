from core.sources.BaseSource import BaseSource
from datetime import datetime
from bs4 import BeautifulSoup

class TokenSniffer(BaseSource):
    url = "https://tokensniffer.com/"

    limit_calls = 2
    limit_period = 3

    def __init__(self,**kwds) -> None:
        for attr in ["proxy","agent"]:
            kwds.pop(attr, None)
            setattr(self,attr,kwds.get(attr,None))


    def address_res(self,address):
        return self.request(f"/token/{address}")
    
    def get(self,address):
        res = self.address_res(address)
        default = dict(
            deployed=0,
            first_seen=0,
            source_md5="",
            similar_count=0,
            similar_viewable=0,
            no_older_tokens=False,
            not_proxy=False,
            not_pausable=False
        )
        if res.status_code == 500:
            # deployed 0 will tell us it hasn't been scanned
            return default
        else:
            try:
                data = self.parse_soup_json(
                    BeautifulSoup(res.text,"html.parser"),
                    "script#__NEXT_DATA__"
                )["props"]["pageProps"]
                token_data = data["token"]
            except Exception as e:
                print(e)
                return default

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
