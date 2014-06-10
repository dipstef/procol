import time
from procol.console import print_line, print_err
from procol.pool import ProcessPool
from procol.pool.future import PoolWorkerError


def print_test(j):
    if j == 2:
        raise Exception('foo')
        pass
    else:
        time.sleep(j)
        pass
    return j


def main():
    pool = ProcessPool(1)
    futures = pool.map_async(print_test, range(10))

    #will wait completion
    for future in futures:
        try:
            print_line(future, future.result)
        except PoolWorkerError:
            print_err(future)
if __name__ == '__main__':
    main()