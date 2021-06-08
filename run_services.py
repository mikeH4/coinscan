from library.BaseSource import RequestPool
from library.Thread import ThreadPool
from services.pull_new import main as pull_new
from services.pull_scanner import main as pull_scanner
from services.update_listings import main as update_listings
from services.update_recent import main as update_recent
from services.update_holders import main as update_holders

if __name__ == "__main__":
    RequestPool._init_proxies()
    tp = ThreadPool()

    t1 = tp.run(pull_new)
    t1 = tp.run(pull_scanner)
    t1 = tp.run(update_listings)
    t1 = tp.run(update_recent)
    t1 = tp.run(update_holders)

    tp.collect()