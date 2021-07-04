import traceback
from library.BaseSource import RequestPool
from library.Thread import ThreadPool
from time import sleep

import settings

import services.pull_new
import services.pull_scanner
import services.poll_listings
import services.poll_verified
import services.update_recent_holders
import services.pull_listing_tokens
import services.sweep_creator
import services.sweep_verified
import services.update_all_holders
import services.pull_token_prices
import services.pull_pairs
import services.sweep_pair_holders
import services.copy_non_existent

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
    ThreadPool.intercept_prints()
    tp = ThreadPool()

    threads_to_run = [
        services.pull_new,
        services.pull_scanner,
        services.poll_listings,
        services.update_recent_holders,
        services.sweep_creator,
        services.poll_verified,
        services.sweep_verified,
        services.pull_listing_tokens,
        services.update_all_holders,
        services.pull_token_prices,
        services.pull_pairs,
        services.sweep_pair_holders,
        services.copy_non_existent,
    ]
    if settings.sandbox == True:
        threads_to_run = [
            # services.pull_new,
            # services.pull_scanner,
            services.poll_listings,
            # services.update_recent_holders,
            # services.sweep_creator,
            # services.poll_verified,
            # services.sweep_verified,
            services.pull_listing_tokens,
            # services.update_all_holders,
            # services.pull_token_prices,
            # services.pull_pairs,
            # services.sweep_pair_holders,
            # services.copy_non_existent,
        ]

    for module in threads_to_run:
        name = module.__name__.split(".")[-1]
        t = tp.run(catching_wrapper(module.main),name=name)

    tp.collect()