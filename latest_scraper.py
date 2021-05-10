from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import json

from modules.requests import get
from modules.db import DB

interval_map = dict(
    m="minutes",
    h="hours",
    d="days",
)
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
            obj = dict(
                address=token["addr"],
                name=token["name"],
                symbol=token["symbol"].upper(),
                chain=chain_map[chain],
                defunct=int(token["defunct"]),
                source_md5=token.get("source_md5",""),
                added=added.timestamp()
            )
            if obj["source_md5"] is None:
                obj["source_md5"] = ""
            
            print(obj["source_md5"])
            db.insert("latest",obj,commit=False,ignore_insert=False)
    print("Updated")    
    db.close()