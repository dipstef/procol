import time
from procol.pool import ProcessPool


def print_test(j):
    print j
    if j == 2:
        raise Exception('foo')
        pass
    else:
        time.sleep(j)
        pass
    return j


def main():
    pool = ProcessPool(1)
    futures = pool.execute_list(print_test, range(10))

    #will wait completion
    for future in futures:
        print future, future.result

if __name__ == '__main__':
    main()