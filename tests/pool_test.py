import time
from procol.console import print_line, print_err
from procol.pool import ProcessPool, PoolWorkerError


def print_test(j):
    if j == 2:
        raise Exception('foo')
    time.sleep(j)
    return j


def _print_futures(futures):
    for future in futures:
        try:
            print_line(future, future.get())
        except PoolWorkerError:
            print_err(future)


def main():
    pool = ProcessPool(5)

    futures = pool.map_async(print_test, range(5))

    futures.results()

    for future in futures:
        try:
            result = future.get()
            print future
        except PoolWorkerError, e:
            print_err(e)

    #print futures

    #pool.map(print_test, range(10))

    #futures = pool.map_async(print_test, range(10))

    #will wait completion
    #_print_futures(futures)

    #futures = pool.map_async(print_test, range(10))

    print 'Completed: '
    futures = pool.map_async(print_test, reversed(range(5)))
    #futures = pool.map_async(print_test, [2])

    for future in futures.iterate_completed():
        print future


if __name__ == '__main__':
    main()