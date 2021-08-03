from library.postgres import DB
from core.Token import TokenMeta

limit = 10000

with DB() as blockchain:
    with DB("bsc") as bsc:
        count = int(bsc.get_all("SELECT COUNT(*) FROM token_meta")[0][0])
        for offset in range(0,count,limit):
            rows = bsc.get_all(f"SELECT * FROM token_meta LIMIT {limit} OFFSET {offset}")
            for row in rows:
                TokenMeta()
                TokenMeta(chain="",f="")