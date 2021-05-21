from contextlib import contextmanager
from time import time

@contextmanager
def timer(description: str) -> None:
    start = time()
    yield
    elapsed_time = round(time() - start,2)

    print(f"{description}: {elapsed_time}")