Procol
======
A collection of function and classes for concurrent processing

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
    assert future.get() is 1


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


Queues
======
Producer consumer queue implementations:

Inter process, the producer is running in a separate thread

.. code-block:: python

    from procol.queue.ipc import ProducerThread

Or Process

.. code-block:: python

    from procol.queue.ipc import ProducerProcess


.. code-block:: python

    def _sleep(j):
        time.sleep(j)
        return j

    >>> producer = ProducerThread(producer=_sleep)
    >>> producer.start()


    def _execute(j):
        result = producer.execute(j)
        print 'Received: ', result

    processes = [Process(target=_execute, args=(i, )) for i in range(5)]
    for process in processes:
        process.start()

    Received:  0
    Received:  1
    Received:  2
    Received:  3
    Received:  4

Between threads in the same process:

Remote using ``multiprocessing`` managers

Start the server:

.. code-block:: python

   from procol.queue.manager import queue_server

   queue_server(ProducerThread(producer=_sleep), port=50000)

Client:

.. code-block:: python

   from procol.queue.manager import queue_client

   queue = queue_client(('server', 5000)


High-performance ``zeromq`` queue:

Inter-process:

.. code-block:: python

    from procol.queue import zero_mq

    >>> producer = zero_mq.ProducerProcess(producer=_sleep)
    >>> producer.start()

    >>> assert producer.execute(1) is 1

Remote:

Server:

.. code-block:: python

   >>> producer = zero_mq.Producer(port=12345)


.. code-block:: python

   >>> producer = zero_mq.Consumer(host='server-address', port=12345)
   >>> assert producer.execute(1) is 1


Scheduler
=========

.. code-block:: python

    from procol.scheduler import schedule, repeat

    def print_hello():
        print 'Hello: ' , datetime.now()

    >>> schedule(print_hello, after=seconds(2))

Repeater

.. code-block:: python

    >>> schedule(print_hello, every=seconds(10), after=seconds(2))