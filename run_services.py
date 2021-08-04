import traceback
from library.Thread import ThreadPool
from time import sleep

import settings

# From Api2
import services.poll_new
import services.poll_pairs
import services.copy_token_prices
import services.sync_listing_tokens

# From Listing Sites
import services.poll_listings

# From BscScan
import services.poll_verified
import services.update_holders

# From BscscanApi
import services.sync_verified


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
    # ThreadPool.intercept_prints()
    tp = ThreadPool()

    threads_to_run = [
        services.copy_token_prices,
        services.poll_listings,
        services.poll_new,
        services.poll_verified,
        services.sync_listing_tokens,
        services.sync_verified,
        services.update_holders,
    ]
    if settings.sandbox == True:
        threads_to_run = [
            services.copy_token_prices,
            services.poll_listings,
            services.poll_new,
            services.poll_verified,
            services.sync_listing_tokens,
            services.sync_verified,
            # services.update_holders,
        ]

    for module in threads_to_run:
        name = module.__name__.split(".")[-1]
        t = tp.run(catching_wrapper(module.main),name=name)

    tp.collect()