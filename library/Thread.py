import sys
from threading import Thread as PythonThread, current_thread
from typing import Callable, Optional

class Thread:
    def __init__(self,pool,thread:PythonThread,name:str) -> None:
        self.pool = pool
        self.thread = thread
        self.thread.name = name
        self.name = name
    
    def wait(self):
        while True:
            self.pool.wait_for_thread(self)

    def start(self):
        self.thread.start()

class ThreadPoolPrintIntercepter():
    original: Optional[Callable] = None

    @staticmethod
    def write(message:str):
        if message != "\n" and message != " ":
            message = f"{current_thread().name} @> {message}"
        assert ThreadPoolPrintIntercepter.original is not None
        ThreadPoolPrintIntercepter.original(message)

class ThreadPool:
    @staticmethod
    def intercept_prints():
        ThreadPoolPrintIntercepter.original = sys.stdout.write
        sys.stdout.write = ThreadPoolPrintIntercepter.write # type: ignore

    def __init__(self) -> None:
        self._active = {}
        self._threads_created = 0
    
    def _decide_name(self,name=None):
        if name is not None:
            return name
        return f"Thread {self._threads_created}"

    def run(self,func,name=None,*args,**kwargs):
        self._threads_created += 1

        thread = Thread(self,
            PythonThread(target=func,args=args,kwargs=kwargs),
            self._decide_name(name)
        )
        self._active[thread] = None

        thread.start()
        return thread
    
    def wait_for_thread(self,thread:Thread):
        del self._active[thread]
        thread.thread.join()
    
    def collect(self):
        active = self._active.copy()
        for thread in active.keys():
            self.wait_for_thread(thread)