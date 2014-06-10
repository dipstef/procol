import multiprocessing
import traceback
from funlib import LambdaFunction


class PoolWorkerError(Exception):
    def __init__(self, *args, **kwargs):
        super(PoolWorkerError, self).__init__(*args, **kwargs)


class PoolFunction(LambdaFunction):
    def __call__(self):
        try:
            result = super(PoolFunction, self).__call__()
            return result
        except:
            name = multiprocessing.current_process().name
            raise PoolWorkerError('{} Error executing: {}\n{}'.format(name, str(self), traceback.format_exc()))


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