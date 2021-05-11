from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import json

from modules.requests import get
from modules.db import DB

chain_map = dict(
    bscTokens="bsc",
    ethTokens="eth"
)
while True:
    db = DB("data/db.db")
    
    res = get("https://tokensniffer.com/tokens/new",wait=10*60)
    
    soup = BeautifulSoup(res.text,"lxml")
    script_content = soup.select("script#__NEXT_DATA__")[0].string
    data = json.loads(script_content)["props"]["pageProps"]
    
    for chain in ["bscTokens","ethTokens"]:
        tokens = data[chain]
        for token in tokens:
            added = datetime.strptime(token["created_at"],"%Y-%m-%dT%H:%M:%S.%fZ")
            latest = dict(
                address=token["addr"],
                name=token["name"],
                symbol=token["symbol"].upper(),
                chain=chain_map[chain],
                added=added.timestamp()
            )
            bscheck = dict(
                address=token["addr"],
                rating="",
                burned_tokens=0,
                total_supply=0,
                holders=0,
            )
            tokensniffer = dict(
                address=token["addr"],
                verified_source=True,
                proxy_contains=True,
                pausable_contains=True,
                defunct=int(token["defunct"]),
                source_md5=token["source_md5"] if token["source_md5"] is not None else "",
            )
            db.insert("latest",obj,commit=False,ignore_insert=True)
            db.insert("bscheck",obj,commit=False,ignore_insert=True)
            db.insert("tokensniffer",obj,commit=False,ignore_insert=True)
    
    print("Updated")
    db.close()