import requests
from ratelimit import limits, sleep_and_retry


@sleep_and_retry
@limits(calls=5, period=1)
def req():
    url = "https://api.bscscan.com/api?module=stats&action=tokensupply&contractaddress=0xe9e7cea3dedca5984780bafc599bd69add087d56&apikey=REDACTED"
    rs = requests.get(url)
    return rs.json()

while True:
    r = req()
    print(r)
    print("Req")