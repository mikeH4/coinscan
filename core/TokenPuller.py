from time import sleep, time

from core.sources.BSCheck import BSCheck
from core.sources.BscScan import BscScan
from core.sources.TokenFomo import TokenFomo
from core.sources.TokenSniffer import TokenSniffer

from library.backoff import backoff
from library.postgres import DB

from datetime import datetime


from core.Token import Token
from core.Address import Address

class TokenPuller:
    def get_existing_addresses(self,of=[],updated_after=None):
        of = list(map(str,of))
        placeholder = self.db.placeholder(len(of))
        sql = f"SELECT address FROM tokens WHERE address IN ({placeholder})"
        if updated_after is not None:
            sql += f" AND updated > {self.db.placeholder(1)}"
            of += [updated_after]
        addrs = [row[0] for row in self.db.get_all(sql,of)]
        return addrs

    def __init__(self, ignore_existing = "recent") -> None:
        tokenfomo = TokenFomo()
        bscheck = BSCheck()
        tokensniffer = TokenSniffer()
        bscscan = BscScan(apikey="REDACTED")

        self.db = DB("tokens")

        while True:
            cycle_start = time()
            data = tokenfomo.get()

            addrs = [row["addr"] for row in data]
            existing_addrs = [] if not ignore_existing else self.get_existing_addresses(
                addrs,
                # In last 1 Hour
                updated_after=(
                    int(datetime.now().timestamp()-(60*60*1))
                    if ignore_existing == "recent"
                    else None
                )
            )
            data_len = len(data)
            
            for i,record in enumerate(data):
                if record["chainId"] != "BSC":
                    continue
                if record["addr"] in existing_addrs:
                    print("Skipped:",record["addr"])
                    continue

                address = Address(record["addr"])
                init_args = dict(
                    address=address,
                    block_time=int(record["blockTime"]),
                    updated=int(datetime.now().timestamp())
                )
                
                # BscScan
                updt,holders = backoff(bscscan.get,address)
                if updt is None:
                    continue
                init_args.update(updt)

                # BSCheck
                init_args.update(bscheck.get(address))
                
                # Token Sniffer
                init_args.update(tokensniffer.get(address))
                
                
                Token(**init_args).insert_or_update(db=self.db)
                for holder in holders:
                    holder.insert_or_update(db=self.db)

                print(f"{i+1}/{data_len}")

                self.db.conn.commit()

                if time() - cycle_start > 60*1.25:
                    break
            
            if time() - cycle_start < 5:
                pass
                # sleep(20)
                # print("Closed")
                break

        self.db.close()