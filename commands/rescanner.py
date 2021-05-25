from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timedelta
from time import time

from core.Holders import Holders
from library.timer import timer
from library.backoff import backoff
from library.postgres import DB

from core.sources.BSCheck import BSCheck
from core.sources.BscScan import BscScan
from core.sources.TokenSniffer import TokenSniffer

from core.Proxies import Proxies
from core.Token import Token

while True:
    with timer("Took"):
        proxies = Proxies.get_all(task="rescanner")

        proxies = [proxy for proxy in proxies if proxy.test()]

        print("Using proxies:")
        print(proxies)
        print("")


        tokens = list(reversed(Token.get_latest(
            limit=None,
            before=(datetime.now()-timedelta(hours=24)).timestamp()
        )))

        remainder = len(tokens) % len(proxies)
        extra = tokens[:remainder]
        tokens = tokens[remainder:]

        each = int(len(tokens) / len(proxies))

        chunks = {}

        for i in range(len(proxies)):
            _from,_to  = [i*each,(i+1)*each]
            chunk = tokens[_from:_to]
            chunks[proxies[i]] = chunk

        chunks[proxies[0]] += extra

        # Chunks created

        def pull_chunk(ip,agent,apikey,tokens):
            bscheck = BSCheck(proxy=ip,agent=agent)
            tokensniffer = TokenSniffer(proxy=ip,agent=agent)
            bscscan = BscScan(apikey=apikey,proxy=ip,agent=agent)

            tokens_len = (len(tokens))

            for i,token in enumerate(tokens):
                desc = f"""
                IP: {ip}
                {i+1}/{tokens_len}
                """
                with timer(desc):
                    with timer("Pulling"):
                        # BscScan
                        args,holders = backoff(bscscan.get,token.address,time=120)
                        attrs = ["total_supply","holders","decimals","description",
                        "bscscan_img","source_verified"]
                        for attr in attrs:
                            setattr(token,attr,args[attr])
                        
                        # BSCheck
                        attrs = ["rating","honeypot_check","owner_renounced",
                        "dev_liquidity_check","lp_check","top_holders_check"]
                        args = bscheck.get(token.address)
                        for attr in attrs:
                            setattr(token,attr,args[attr])
                        
                        # TokenSniffer
                        attrs = ["deployed","first_seen","source_md5","similar_count",
                        "similar_viewable","no_older_tokens","not_proxy","not_pausable"]
                        args = tokensniffer.get(token.address)
                        for attr in attrs:
                            setattr(token,attr,args[attr])

                        token.updated = time()

                        with timer("DB Updates"):
                            # Updates
                            with DB("tokens") as db:
                                Holders.delete_all(token.address,db=db)
                                for holder in holders:
                                    holder.insert_or_update(db=db)
                                token.insert_or_update(db=db)
                
        with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
            processes = []
            for ip,tokens in chunks.items():
                processes.append(executor.submit(pull_chunk,ip.ip,ip.agent,ip.apikey,tokens))

            for future in as_completed(processes):
                print(future.result())