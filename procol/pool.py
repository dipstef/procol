import atexit
import multiprocessing
import traceback

from funlib import LambdaFunction


class PoolWorkerException(Exception):
    def __init__(self, *args, **kwargs):
        super(PoolWorkerException, self).__init__(*args, **kwargs)


class PoolFunction(LambdaFunction):
    def __call__(self):
        try:
            result = super(PoolFunction, self).__call__()
            return result
        except:
            name = multiprocessing.current_process().name
            raise PoolWorkerException('{} Error executing: {}\n{}'.format(name, str(self), traceback.format_exc()))


class Future(object):
    def __init__(self, function, async_result):
        super(Future, self).__init__()
        self._apply_result = async_result
        self._result = None
        self._function = function
        self.completed = False

    def wait(self):
        if not self.completed:
            self._result = self._apply_result.get()
            self.completed = True

    @property
    def result(self):
        self.wait()
        return self._result

    def __str__(self):
        return str(self._function)


class Futures(object):
    def __init__(self, futures):
        self._futures = futures

    def results(self):
        return list(self.iterate_results())

    def iterate_results(self):
        return (future.result for future in self._futures)

    def __iter__(self):
        return iter(self._futures)


class ProcessPool(object):

    def __init__(self, max_size=None):
        self._pool = multiprocessing.Pool(max_size)
        atexit.register(lambda: self._pool.terminate())

    def execute(self, function, args=(), kwargs=None):
        kwargs = kwargs or {}
        function = PoolFunction(function, *args, **kwargs)
        async_result = self._pool.apply_async(func=function)

        return Future(function, async_result)

    def map(self, function, args_list):
        'Will stop in case a worker raises an exception is raised in a worker'
        futures = self.execute_list(function, args_list)
        return futures.results()

    def execute_list(self, function, args_list):
        futures = [self.execute(function, _args_tuple(args)) for args in args_list]

        return Futures(futures)

    def iterate_results(self, function, args_list):
        return self.execute_list(function, args_list).iterate_results()

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