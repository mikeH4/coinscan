import requests
from time import time,sleep

last_request = 0
useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"

def get(url,params={},headers={},cookies={},wait=0):
    global last_request
    sleep(max(0,wait-(time()-last_request)))
    last_request = time()

    print("Request: ", url)

    if useragent is not None:
        headers["User-Agent"] = useragent

    raw_content = requests.get(
        url,
        headers=headers,
        params=params,
        cookies=cookies
    )
    return raw_content