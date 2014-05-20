from procol.queue import processes, threads
from procol.queue.threads import ThreadCallableRequests
from procol.queue.zero_mq import ProducerConsumerZeroMq


def produce(request):
    #print 'Received', request
    #print 'Sending Back', request
    return request


def _test_queue(requests):
    assert (1, 2) == requests.execute((1, 2))
    result = requests.execute((3, 4))
    assert (3, 4) == result
    assert (5, 6) == requests.execute((5, 6))


def _test_process_queue(requests):
    processes.ProducerConsumerProcess(requests, produce)
    _test_queue(requests)

    requests.close()


def _test_thread_queue(requests):
    threads.ProducerConsumerThread(requests, produce)
    _test_queue(requests)
    requests.close()


def _test_thread_pool():
    requests = ThreadCallableRequests()

    threads.ProducerConsumerThread(requests, lambda function: produce(function()))
    assert (1, 2) == requests.execute(lambda: (1, 2))
    result = requests.execute(lambda: (3, 4))
    assert (3, 4) == result
    assert (5, 6) == requests.execute(lambda: (5, 6))
    requests.close()


def main():
    _test_process_queue(ProducerConsumerZeroMq())
    _test_process_queue(processes.ProducerConsumer())

    _test_thread_queue(threads.ProducerConsumerThreadQueue())
    _test_thread_pool()

if __name__ == '__main__':
    main()