import multiprocessing
import traceback
from funlib import Lambda, Function


class PoolWorkerError(Exception):

    def __init__(self, cause, traceback_string):
        super(PoolWorkerError, self).__init__(cause, traceback_string)
        self.cause = cause
        self.traceback = traceback_string

        self.message = traceback_string

    def __str__(self):
        return self.traceback


class PoolFunction(Lambda):

    def __init__(self, fun, *args, **kwargs):
        super(PoolFunction, self).__init__(fun, *args, **kwargs)

    def __call__(self):
        try:
            result = super(PoolFunction, self).__call__()
            return result
        except BaseException, e:
            name = multiprocessing.current_process().name
            traceback_string = '{} Error executing: {}\n{}'.format(name, str(self), traceback.format_exc())

            error = PoolWorkerError(e, traceback_string)
            #error.error = e
            raise error


class Future(Function):

    def __init__(self, function):
        super(Future, self).__init__(function)
        self._result = None
        self._error = None
        self._completed = False

    def get(self):
        if not self.is_executed():
            self._get()

        if self._error:
            raise self._error
        return self._result

    def _get(self):
        try:
            self._result = self._get_result()
        except BaseException, e:
            self._error = e
        finally:
            self._completed = True

    def __call__(self):
        return self.get()

    def _get_result(self):
        return self._fun()

    def is_executed(self):
        return self._completed

    def __str__(self):
        if self.is_executed():
            if not self._error:
                return '{function}: {outcome}'.format(function=self._fun, outcome=self._result)
            else:
                return '{function} Failed:  {error}'.format(function=self._fun, error=repr(self._error.cause))
        else:
            return '{function}: not executed'.format(function=self._fun)

    def __repr__(self):
        return str(self.__class__.__name__) + ' ' + str(self)


class PoolFuture(Future):

    def __init__(self, pool, (function, args, kwargs)):
        pool_function = PoolFunction(function, *args, **kwargs)
        super(PoolFuture, self).__init__(pool_function)
        self._pool_execution = pool.apply_async(self._fun)

    def _get_result(self):
        return self._pool_execution.get()

    def is_executed(self):
        executed = self._completed

        if not executed:
            executed = self._pool_execution.ready()

            if executed:
                self._get()

        return executed


class Futures(object):
    def __init__(self, futures):
        self._futures = futures

    def results(self):
        return list(self.iterate_results())

    def iterate_results(self):
        return (future.get() for future in self._futures)

    def iterate_completed(self):
        remaining, completed = list(self._futures), []

        while len(completed) < len(self._futures):
            for index, future in enumerate(remaining):
                if future.is_executed():
                    completed.append(future)
                    del remaining[index]
                    yield future

    def __iter__(self):
        return iter(self._futures)

    def __str__(self):
        return 'Futures: [\n%s\n]' % '\n'.join((str(future) for future in self._futures))