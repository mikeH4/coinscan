from library.Thread import ThreadPool
from services.pull_new import main as pull_new
from services.pull_scanner import main as pull_scanner

if __name__ == "__main__":
    tp = ThreadPool()

    t1 = tp.run(pull_new)
    t1 = tp.run(pull_scanner)

    tp.collect()