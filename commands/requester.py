from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timedelta
from time import time,sleep

from core.Holders import Holders
from library.timer import timer
from library.backoff import backoff
from library.postgres import DB

from core.sources.BSCheck import BSCheck
from core.sources.BscScan import BscScan
from core.sources.TokenSniffer import TokenSniffer

from core.Proxies import Proxies
from core.TokenRequest import TokenRequest
from core.Token import Token

while True:
    with timer("Took"):
        token_requests = TokenRequest.get_latest(limit=1000)

        if len(token_requests) < 1:
            print("Sleeping for 1 min, nothing to do: bored")
            sleep(60*1)

        proxies = Proxies.get_all(task="request")

        proxies = [proxy for proxy in proxies if proxy.test()]

        print("Using proxies:")
        print(proxies)
        print("")

        remainder = len(token_requests) % len(proxies)
        extra = token_requests[:remainder]
        token_requests = token_requests[remainder:]

        each = int(len(token_requests) / len(proxies))

        chunks = {}

        for i in range(len(proxies)):
            _from,_to  = [i*each,(i+1)*each]
            chunk = token_requests[_from:_to]
            chunks[proxies[i]] = chunk

        chunks[proxies[0]] += extra

        # Chunks created

        def pull_chunk(ip,agent,apikey,token_requests):
            bscheck = BSCheck(proxy=ip,agent=agent)
            tokensniffer = TokenSniffer(proxy=ip,agent=agent)
            bscscan = BscScan(apikey=apikey,proxy=ip,agent=agent)

            token_requests_len = (len(token_requests))

            for i,token_request in enumerate(token_requests):
                desc = f"""
                IP: {ip}
                {i+1}/{token_requests_len}
                """
                with timer(desc):
                    init_args = dict(
                        address=token_request.address,
                        block_time=0,
                        updated=int(datetime.now().timestamp())
                    )

                    # BscScan
                    args,holders = backoff(bscscan.get,token_request.address)
                    if args is None:
                        token_request.remove()
                        continue                        
                    init_args.update(args)

                    # BSCheck
                    args = bscheck.get(token_request.address)
                    init_args.update(args)

                    # TokenSniffer
                    args = tokensniffer.get(token_request.address)
                    init_args.update(args)

                    with DB("tokens") as db:
                        Token(**init_args).insert_or_update(db=db)
                        for holder in holders:
                            holder.insert_or_update(db=db)
                        
                        token_request.remove(db=db)

                        db.conn.commit()
                
        with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
            processes = []
            for ip,token_requests in chunks.items():
                processes.append(executor.submit(pull_chunk,ip.ip,ip.agent,ip.apikey,token_requests))

            for future in as_completed(processes):
                print(future.result())