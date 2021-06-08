from library.BaseSource import RequestPool
from library.Thread import ThreadPool
from time import sleep

from services.pull_new import main as pull_new
from services.pull_scanner import main as pull_scanner
from services.pull_creator import main as pull_creator
from services.update_listings import main as update_listings
from services.update_recent import main as update_recent
from services.update_holders import main as update_holders

def catching_wrapper(func):
    def wrapper(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            print(e)
            print("Thread Exception Caught, will restart in 10 sec")
            sleep(10)
    return wrapper



if __name__ == "__main__":
    RequestPool._init_proxies()
    tp = ThreadPool()

    threads_to_run = [
        pull_new,
        pull_scanner,
        pull_creator,
        update_listings,
        update_recent,
        update_holders
    ]

    for func in threads_to_run:
        t = tp.run(catching_wrapper(func))

    tp.collect()