from contextlib import contextmanager
from time import time,sleep

class Repeater:
    def __init__(self,min=1*60,max=2*60) -> None:
        self.min = min
        self.max = max

        self.last_release = 0
        
        self.manager = self.manager_factory()

    def manager_factory(self):
        @contextmanager
        def manager():
            # If requests are too less
            sleep_for = self.min - (time() - self.last_release)
            if sleep_for > 0:
                print(f"Sleep for {sleep_for}")
                sleep(sleep_for)
            self.last_release = time()
            yield
        return manager

    def should_repeat(self):
        return (time() - self.last_release) > self.max