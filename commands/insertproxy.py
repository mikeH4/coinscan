from library.postgres import DB
from time import time
from library.Proxies import Proxies


insert = {}
insert["ip"] = input("IP?")
insert["port"] = input("Port?")
insert["bscscan_apikey"] = input("BscAcan Apikey?")
insert["cmc_apikey"] = input("CMC Apikey?")

insert["agent"] = Proxies.random_agent()
insert["added"] = time()

Proxies(**insert).insert()