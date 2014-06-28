import atexit
import multiprocessing

from .future import PoolFunction, Future, PoolFuture
from .future import Futures, PoolWorkerError


class ProcessPool(object):

    def __init__(self, max_size=None):
        self._pool = multiprocessing.Pool(max_size)
        atexit.register(lambda: self._pool.terminate())

    def execute(self, function, args=(), kwargs=None):
        return PoolFuture(self._pool, (function, args, kwargs or {}))

    def map(self, function, args_list):
        'Will stop in case a worker raises an exception is raised in a worker'
        futures = self.map_async(function, args_list)
        return futures.results()

    def map_async(self, function, args_list):
        futures = [self.execute(function, _args_tuple(args)) for args in args_list]

        return Futures(futures)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *args):
        if exc_type and issubclass(exc_type, BaseException):
            self.terminate()
        else:
            self.close()

    def close(self):
        self._pool.close()
        self._pool.join()

    def terminate(self):
        self._pool.terminate()
        self._pool.join()


def _args_tuple(args):
    return args if isinstance(args, tuple) else (args, )