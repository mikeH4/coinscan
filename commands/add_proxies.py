from ipaddress import ip_address
from library.postgres import DB
from time import time

from core.Proxies import Proxies

proxies = Proxies.get_all()

proxy_by_ip = {}

active = set()
for proxy in proxies:
    active.add(proxy.ip)
    proxy_by_ip[proxy.ip] = proxy

print("Proxies Active: ")
print(list(active))

new_ips = set()
apikeys = {}
tasks = {}
n = ""
while True:
    print("Add new IP in format IP:port (n to exit)")
    inpt = input("")
    if inpt.lower() == "n":
        break

    try:
        ip,port = inpt.split(":",2)
        print(ip,port)
        int(port)
        ip_address(ip)
    except Exception as e:
        print("Invalid format")
        continue

    if inpt in active or input in new_ips:
        print("Already exists")
        continue

    apikey = input("Enter API Key: ")
    
    task = None
    while task not in ["rescanner","request"]:
        task = input("Enter Task: ")
    
    apikeys[inpt] = apikey
    tasks[inpt] = task
    new_ips.add(inpt)

db = DB("tokens")
added = set()
removed = set()
for ip in new_ips.union(active):
    if Proxies.test_proxy(ip):
        if ip in active:
            continue
        Proxies(
            ip=ip,
            agent=Proxies.random_agent(),
            apikey=apikeys[ip],
            task=tasks[ip],
            status="active",
            added=time(),
        ).insert(db)
        added.add(ip)
    elif ip in active:
        removed.add(ip)
        proxy_by_ip[ip].remove()

print("Removed:")
print(list(removed))
print("Not Passed:")
print(list(new_ips - added))

print("Added:")
print(list(added))

db.close()