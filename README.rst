Procol
======

A library for concurrent processing:
Includes producer-consumer for in-inter process communication, as well remote implementations based on zero-mq
and multiprocessing remote manager.
Other features include scheduling and a pool worker

Pool
====
A friendly wrapper of the ``multiprocessing`` Pool

.. code-block:: python

    from procol.pool import ProcessPool

    def _sleep(j):
        if j == 2:
            raise Exception('foo')
        time.sleep(j)
        return j

    >>> pool = ProcessPool(5)


Returns futures objects

.. code-block:: python

    >>> futures = pool.map_async(print_test, range(5))

    for future in futures:
        try:
            result = future.get()
            print future
        except PoolWorkerError, e:
            print_err(e)

    print_test(0): 0
    print_test(1): 1

When an error is raised from a worker a traceback from the call originating the error is also returned

.. code-block:: python

    PoolWorker-3 Error executing: print_test(2)
    Traceback (most recent call last):
      File "../procol/pool/future.py", line 26, in __call__
        result = super(PoolFunction, self).__call__()
      File "build/bdist.macosx-10.9-intel/egg/funlib/__init__.py", line 55, in __call__
        return self._fun(*self.args, **self.kwargs)
      File "../tests/pool_test.py", line 8, in print_test
        raise Exception('foo')
    Exception: foo

    print_test(3): 3
    print_test(4): 4
    print_test(5): 5

However if you want to retrieve the results of the futures the execution stops as soon an error is encountered

.. code-block:: python

    >>> results = futures.results()

    PoolWorker-3 Error executing: print_test(2)
    Traceback (most recent call last):
      File "../procol/pool/future.py", line 26, in __call__
        result = super(PoolFunction, self).__call__()
      File "build/bdist.macosx-10.9-intel/egg/funlib/__init__.py", line 55, in __call__
        return self._fun(*self.args, **self.kwargs)
      File "../tests/pool_test.py", line 8, in print_test
        raise Exception('foo')
    Exception: foo