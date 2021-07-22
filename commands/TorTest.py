from concurrent.futures.thread import ThreadPoolExecutor
from core.sources.Test import IfConfig
from library.timer import timer
from library.BaseSource import RequestPool
RequestPool._init_proxies()

ip = IfConfig()

test_size = 200

with timer("Tor Pool") as increment:
    with ThreadPoolExecutor(max_workers=20) as exec:
        for i in range(test_size):
            exec.submit(ip.get)
    increment(test_size)

with timer("Proxy Pool") as increment:
    ip.request_manager = RequestPool
    with ThreadPoolExecutor(max_workers=20) as exec:
        for i in range(test_size):
            exec.submit(ip.get)
    increment(test_size)