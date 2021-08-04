import requests
from urllib.parse import urlencode

def get(url,params={},headers={},json={}):
    print(f"Request: {url}?{urlencode(params)}")

    res = requests.get(
        url,
        params=params,
        headers=headers,
        json=None if json == {} else json
    )
    return res