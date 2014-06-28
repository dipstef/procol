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
            raise ValueError('two')
        time.sleep(j)
        return j

    >>> pool = ProcessPool(5)

.. code-block:: python


Returns futures for async operations

.. code-block:: python
    >>> future = pool.execute(_sleep, args=(1,))
    assert 1 = future.get(


.. code-block:: python

    >>> futures = pool.map_async(_sleep, range(5))

    for future in futures:
        try:
            result = future.get()
            print future
        except PoolWorkerError, e:
            print_err(e)

    _sleep(0): 0
    _sleep(1): 1

When an error is raised from a worker a traceback from the call originating the error is also returned

.. code-block:: python

    PoolWorker-3 Error executing: _sleep(2)
    Traceback (most recent call last):
    ......File "..pool_test.py", line 8, in _sleep
        raise ValueError('two')
    ValueError: two

    _sleep(3): 3
    _sleep(4): 4
    _sleep(5): 5

However if you want to retrieve the results of the futures the execution stops as soon an error is encountered

.. code-block:: python

    >>> results = futures.results()

    PoolWorker-3 Error executing: _sleep(2)
    Traceback (most recent call last):
    ......File "..pool_test.py", line 8, in _sleep
    raise ValueError('two')
    ValueError: two

Has the exact behavior as:

.. code-block:: python

   >>> pool.map(_sleep, range(5))

Futures can be iterated in order of completion

.. code-block:: python

    futures = pool.map_async(_sleep, reversed(range(5)))
    for future in futures.iterate_completed():
        print future

    _sleep(2) failed:  ValueError('two',)
    _sleep(0): 0
    _sleep(1): 1
    _sleep(3): 3
    _sleep(4): 4
