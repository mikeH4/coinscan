from contextlib import contextmanager
from library.database.postgres import DB
from time import time,sleep

class Repeater:
    def __init__(self, *,
        min: int = 1*60,
        max: int = 2*60,
        commit_every: int = 5
    ) -> None:
        self.min = min
        self.max = max
        self.commit_every = commit_every

        self.last_release = 0
        self.not_committed_since = 0
        
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

    def loop(self):
        # If requests are too less
        sleep_for = self.min - (time() - self.last_release)
        if sleep_for > 0:
            print(f"Sleep for {sleep_for}")
            sleep(sleep_for)
        self.last_release = time()
        return True

    def should_repeat(self):
        return (time() - self.last_release) > self.max
    
    def commit(self, db: DB):
        self.not_committed_since += 1
        if self.not_committed_since < self.commit_every: return
        
        assert self.not_committed_since == self.commit_every
        
        print("Repeater: commit")
        db.conn.commit()
        self.not_committed_since = 0