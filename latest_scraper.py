from bs4 import BeautifulSoup
from datetime import datetime,timedelta

from modules.requests import get
from modules.db import DB

db = DB("data/db.db")

interval_map = dict(
    m="minutes",
    h="hours",
    d="days",
)
while True:
    res = get("https://tokensniffer.com/tokens/new",wait=10*60)
    soup = BeautifulSoup(res.text,"lxml")
    for token in soup.select("table > tbody > tr"):
        cells = token.select("th,td")
        added_str = cells[3].get_text()[:-4]

        kwargs = {}
        kwargs[interval_map[added_str[-1]]] = int(added_str[:-1])
        delta = timedelta(**kwargs)

        added = (datetime.now() - delta).timestamp()

        obj = dict(
            name=cells[0].get_text(),
            symbol=cells[1].get_text().upper(),
            address=cells[2].get_text(),
            added=added
        )
        db.insert("latest",obj,commit=False,ignore_insert=True)
    db.conn.commit()

db.close()