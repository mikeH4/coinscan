from contextlib import contextmanager
from time import time


@contextmanager
def timer(description: str):
    start = time()
    items = 0
    def increment(by: int):
        nonlocal items
        items += by
        min_since_start = (time()-start)/60
        items_avg = round(items/min_since_start,2)
        print(f"{description}: {items} entered in {round(min_since_start,2)} min, Avg {items_avg} per min")
        return items
    yield increment
    elapsed_time = round((time() - start)/60,2)

    print(f"{description}: {elapsed_time} # {items} items")