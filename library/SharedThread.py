from multiprocessing import Process, Manager, Lock

class Thread:
    def __init__(self,pool,process:Process,name:str) -> None:
        self.pool = pool
        self.process = process
        self.name = name
    
    def wait(self):
        self.pool.wait_for_thread(self)

    def start(self):
        self.process.start()

class ThreadPool:
    def __init__(self) -> None:
        self._active = {}
        self._threads_created = 0

        self.manager = Manager()
        
    
    def _decide_name(self,name=None):
        if name is not None:
            return name
        return f"Thread {self._threads_created}"

    def run(self,func:function,name=None,*args,**kwargs):
        self._threads_created += 1

        thread = Thread(self,
            Process(target=func,args=args,kwargs=kwargs),
            self._decide_name(name)
        )
        self._active[thread] = None

        thread.start()
        return thread
    
    def wait_for_thread(self,thread:Thread):
        del self._active[thread]
        thread.process.join()
    
    def collect(self):
        for thread in self._active.keys():
            self.wait_for_thread(thread)