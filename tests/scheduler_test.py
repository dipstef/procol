from dated.normalized import utc
from dated.date_time import seconds
import time
from procol.scheduler import schedule


def main():
    def print_hello(secs):
        print 'Hello every %d seconds : %s ' % (secs, utc.now())

    schedule(lambda: print_hello(2), after=seconds(2), repeat=True)

    time.sleep(10)

if __name__ == '__main__':
    main()