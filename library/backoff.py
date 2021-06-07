from time import sleep
import traceback

def backoff(func,*args,time = 60):
    while True:
        try:
            return func(*args)
        except Exception as e:
            traceback.print_exc()
            print(e)
            print("Backing off...")
            sleep(time)