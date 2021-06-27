import requests
from urllib.parse import urlencode

def get(url,proxy,params={},headers={},cookies={},json={}):
    headers["User-Agent"] = proxy.agent

    req_proxy = None
    # Empty Proxy means self
    if proxy.ip != "":
        req_proxy = { 
            "http"  : f"http://{proxy.ip}:{proxy.port}", 
            "https" : f"http://{proxy.ip}:{proxy.port}",
        }

    print(f"Request from {proxy}: {url}?{urlencode(params)}",)

    print(req_proxy)
    res = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        proxies=req_proxy,
        json=json
    )
    return res