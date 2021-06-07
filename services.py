from library.SharedThread import ThreadPool
from services.pull_new import pull_new

if __name__ == "main":
    tp = ThreadPool()

    t1 = tp.run(pull_new)

    tp.collect()