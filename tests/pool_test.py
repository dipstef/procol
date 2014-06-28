import time
from procol.console import print_line, print_err
from procol.pool import ProcessPool, PoolWorkerError


def _sleep(j):
    if j == 2:
        raise ValueError('two')
    time.sleep(j)
    return j


def _print_futures(futures):
    for future in futures:
        try:
            result = future.get()
            print future
        except PoolWorkerError, e:
            print_err(e)


def _iterate_features(pool):
    futures = pool.map_async(_sleep, range(5))
    _print_futures(futures)


def main():
    pool = ProcessPool(5)

    #_iterate_features(pool)

    futures = pool.map_async(_sleep, reversed(range(5)))
    for future in futures.iterate_completed():
        print future


if __name__ == '__main__':
    main()