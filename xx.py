from multiprocessing import Process, Manager, Lock
from time import sleep

class X:
    @staticmethod
    def prepare(d,lock,manager):
        X.d = d
        X.lock = lock
        X.manager = manager
        X.f()
    
    @staticmethod
    def f():
        for i in range(5):
            x = X.d["a"][0]

if __name__ == '__main__':
    manager = Manager()
    d = manager.dict({
        "a": manager.list([0]),
    })
    lock = Lock()

    num = 5
    processes = []
    for i in range(num):
        p = Process(target=X.prepare,args=(d,lock,manager))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
    
    print(d["a"][0])