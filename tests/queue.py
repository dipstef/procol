from procol.queue.manager import queue_manager_process
from procol.queue import ipc, threads, zero_mq, ProducerThread, ProducerProcess
from procol.queue.threads import CallableRequests, CallableRequestsThread


def produce(request):
    if request == (0, 0):
        raise ValueError((0,0))
    return request


def _test_queue(requests):
    assert (1, 2) == requests.execute((1, 2))
    result = requests.execute((3, 4))
    assert (3, 4) == result
    assert (5, 6) == requests.execute((5, 6))
    try:
        requests.execute((0, 0))
        assert False
    except ValueError, e:
        assert e.message == (0, 0)

    requests.close()


def _test_requests(requests):
    requests.start()
    _test_queue(requests)


def _test_process_queue(request_class):
    _test_requests(ProducerProcess(request_class, producer=produce))


def _test_thread_queue(request_class):
    _test_requests(ProducerThread(request_class, producer=produce))


def _test_thread_pool():
    requests = CallableRequestsThread(producer=lambda function: produce(function()))

    requests.start()

    result = requests.execute(lambda: (1, 2))
    assert (1, 2) == result
    result = requests.execute(lambda: (3, 4))
    assert (3, 4) == result
    assert (5, 6) == requests.execute(lambda: (5, 6))

    requests.close()


def _remote_manager_queue():
    queue = ProducerThread(ipc.ProducerConsumer, producer=produce)

    queue_manager = queue_manager_process(queue)
    return queue_manager


def _test_zero_mq():
    requests = zero_mq.ProducerThread(producer=produce)
    _test_requests(requests)
    requests.close()


def main():
    _test_zero_mq()
    _test_process_queue(ipc.ProducerConsumer)
    _test_queue(_remote_manager_queue())

    _test_thread_queue(threads.ProducerConsumer)
    _test_thread_pool()

if __name__ == '__main__':
    main()