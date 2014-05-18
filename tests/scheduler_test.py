from procol.scheduler import schedule_every


def main():
    from datelib.normalized import utc

    def print_hello(seconds):
        print 'Hello every %d seconds : %s: ' % (seconds, utc.now())

    #print utc.now()

    schedule_every(2, lambda: print_hello(2), daemon=False)

    #schedule_function(10, lambda: print_hello(10))
    #schedule_function(5, lambda: print_hello(5))
    print 'OK'
    print 'END'

if __name__ == '__main__':
    main()