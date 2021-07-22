from concurrent.futures.thread import ThreadPoolExecutor
from core.sources.Test import Google, IfConfig
from library.timer import timer
from library.BaseSource import RequestPool,TorRequestPool
RequestPool._init_proxies()

ip = IfConfig()
ip.request_manager = TorRequestPool
g = Google()
g.request_manager = TorRequestPool

test_size = 5

with timer("Tor Pool") as increment:
    with ThreadPoolExecutor(max_workers=25) as exec:
        for i in range(test_size):
            exec.submit(ip.get)
            exec.submit(g.get)
    increment(test_size)

ip.request_manager = RequestPool
g.request_manager = RequestPool

with timer("Proxy Pool") as increment:
    with ThreadPoolExecutor(max_workers=25) as exec:
        for i in range(test_size):
            exec.submit(ip.get)
            exec.submit(g.get)
    increment(test_size)