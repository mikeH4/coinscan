import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from db import DB

db = DB("db.db")

def find_symbol(regex,text,flags=0):
    blacklisted = ["BSC","ATH","AMA","UTC","LP","MC","IS","TG","UR","PM","EN"]
    not_before_token = ["dev","huge","New","this","The","This","charity","stock","DeFi","following","owned"]
    token_regex = "\\b([A-Z]+)(?= token\\b)"
    found = re.search(regex,text,flags=flags)
    if found:
        sym = found[0].strip()
        if sym in blacklisted or len(sym) <= 1:
            return None
        if regex == "\\b([A-Z]+)(?= token\\b)" and sym in not_before_token:
            return None
        if sym[0] == "$":
            sym = sym[1:].upper()
        return sym
    return None

from pprint import pprint
for row in db.get_all("SELECT * FROM posts"):
    id = row[0]
    title = row[1]
    body = row[4]
    html = row[5]
    matchers = [
        ["\\B(\$[A-Z]+)\\b", 0], # Matches for Capital Dollar
        ["\\B(\$[A-Z]+)\\b",re.IGNORECASE], # Matches for lowercase $
        ["\\b([A-Z]+)\\b",0], # upper case
        ["\\b([A-Z]+)(?= token\\b)",re.IGNORECASE] # * token
    ]
    symbol = None
    for regex,flags in matchers:
        for text in [title,body]:
            symbol = find_symbol(regex,text,flags)
            if symbol is not None:
                break
        if symbol is not None:
            break
    
    print(symbol,f"https://reddit.com/r/cryptomoonshots/comments/{id}")
    print("")

    soup = BeautifulSoup(html.encode("utf-8"), "lxml")
    for link in soup.find_all("a", href=True):
        href = urlparse(link.attrs["href"])
        domain = href.netloc
        pages = href.path.split("/")
        pprint(domain)
        if domain == "bscscan.com" and pages[1] == "address":
            print(pages[2])
        elif domain == "poocoin.app" and pages[1] == "tokens":
            print("-----" * 10*10*10)
            print(pages[2])