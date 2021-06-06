import requests

def get(url,proxy,params={},headers={},cookies={}):
    headers["User-Agent"] = proxy.agent

    req_proxy = None
    # Empty Proxy means self
    if proxy.ip != "":
        req_proxy = { 
            "http"  : f"http://{proxy.ip}:{proxy.port}", 
            "https" : f"http://{proxy.ip}:{proxy.port}",
        }
    
    return requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        proxy=req_proxy,
    )