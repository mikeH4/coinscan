from functools import wraps
from math import floor

import time
import sys
import threading

class RateLimitException(Exception):
    '''
    Rate limit exception class.
    '''
    def __init__(self, message, period_remaining):
        '''
        Custom exception raise when the number of function invocations exceeds
        that imposed by a rate limit. Additionally the exception is aware of
        the remaining time period after which the rate limit is reset.

        :param string message: Custom exception message.
        :param float period_remaining: The time remaining until the rate limit is reset.
        '''
        super(RateLimitException, self).__init__(message)
        self.period_remaining = period_remaining

# Use monotonic time if available, otherwise fall back to the system clock.
now = time.monotonic if hasattr(time, 'monotonic') else time.time

class RateLimitDecorator(object):
    '''
    Rate limit decorator class.
    '''
    def __init__(self, calls=15, period=900, clock=now, raise_on_limit=True):
        '''
        Instantiate a RateLimitDecorator with some sensible defaults. By
        default the Twitter rate limiting window is respected (15 calls every
        15 minutes).

        :param int calls: Maximum function invocations allowed within a time period. Must be a number greater than 0.
        :param float period: An upper bound time period (in seconds) before the rate limit resets. Must be a number greater than 0.
        :param function clock: An optional function retuning the current time. This is used primarily for testing.
        :param bool raise_on_limit: A boolean allowing the caller to avoiding rasing an exception.
        '''
        self.clamped_calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = period
        self.clock = clock
        self.raise_on_limit = raise_on_limit

        # Initialise the decorator state.
        self.last_reset = {}
        self.num_calls = {}
        self.init_thread_slot()

        # Add thread safety.
        self.lock = threading.RLock()

    def thread_id(self):
        return threading.current_thread().ident

    def init_thread_slot(self):
        thread_id = self.thread_id()
        if thread_id not in self.last_reset:
            self.last_reset[thread_id] = self.clock()
        if thread_id not in self.num_calls:
            self.num_calls[thread_id] = self.clock()


    def __call__(self, func):
        '''
        Return a wrapped function that prevents further function invocations if
        previously called within a specified period of time.

        :param function func: The function to decorate.
        :return: Decorated function.
        :rtype: function
        '''
        @wraps(func)
        def wrapper(*args, **kargs):
            '''
            Extend the behaviour of the decoated function, forwarding function
            invocations previously called no sooner than a specified period of
            time. The decorator will raise an exception if the function cannot
            be called so the caller may implement a retry strategy such as an
            exponential backoff.

            :param args: non-keyword variable length argument list to the decorated function.
            :param kargs: keyworded variable length argument list to the decorated function.
            :raises: RateLimitException
            '''
            with self.lock:
                self.init_thread_slot()

                period_remaining = self.__period_remaining()
                print(period_remaining)

                # If the time window has elapsed then reset.
                if period_remaining <= 0:
                    self.num_calls[self.thread_id()] = 0
                    self.last_reset[self.thread_id()] = self.clock()

                print("CALL")
                # Increase the number of attempts to call the function.
                self.num_calls[self.thread_id()] += 1

                # If the number of attempts to call the function exceeds the
                # maximum then raise an exception.
                if self.num_calls[self.thread_id()] > self.clamped_calls:
                    if self.raise_on_limit:
                        raise RateLimitException('too many calls', period_remaining)
                    return

            return func(*args, **kargs)
        return wrapper

    def __period_remaining(self):
        '''
        Return the period remaining for the current rate limit window.

        :return: The remaing period.
        :rtype: float
        '''
        elapsed = self.clock() - self.last_reset[self.thread_id()]
        return self.period - elapsed

def sleep_and_retry(func):
    '''
    Return a wrapped function that rescues rate limit exceptions, sleeping the
    current thread until rate limit resets.

    :param function func: The function to decorate.
    :return: Decorated function.
    :rtype: function
    '''
    @wraps(func)
    def wrapper(*args, **kargs):
        '''
        Call the rate limited function. If the function raises a rate limit
        exception sleep for the remaing time period and retry the function.

        :param args: non-keyword variable length argument list to the decorated function.
        :param kargs: keyworded variable length argument list to the decorated function.
        '''
        while True:
            try:
                return func(*args, **kargs)
            except RateLimitException as exception:
                time.sleep(exception.period_remaining)
    return wrapper

limits = RateLimitDecorator