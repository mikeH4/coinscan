import traceback
from library.BaseSource import RequestPool
from library.Thread import ThreadPool
from time import sleep

from services.pull_new import main as pull_new
from services.pull_scanner import main as pull_scanner
from services.pull_creator import main as pull_creator
from services.update_listings import main as update_listings
from services.recently_verified import main as recently_verified
from services.update_holders import main as update_holders
from services.update_verified import main as update_verified

def catching_wrapper(func):
    def wrapper(*args,**kwargs):
        while True:
            try:
                return func(*args,**kwargs)
            except Exception as e:
                print(e)
                traceback.print_exc()
                print("Thread Exception Caught, will restart in 10 sec")
                sleep(10)
    return wrapper



if __name__ == "__main__":
    RequestPool._init_proxies()
    tp = ThreadPool()

    threads_to_run = [
        pull_new,
        pull_scanner,
        update_listings,
        update_holders,
        pull_creator,
        recently_verified,
        update_verified,
    ]

    for func in threads_to_run:
        t = tp.run(catching_wrapper(func))

    tp.collect()