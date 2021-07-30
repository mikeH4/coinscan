import requests
from urllib.parse import urlencode

def get(url,params={},headers={},cookies={},json={}):
    print(f"Request: {url}?{urlencode(params)}")

    res = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        json=None if json == {} else json
    )
    return res