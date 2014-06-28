from procol.queue.manager import queue_manager_process
from procol.queue import ipc, threads, zero_mq, ProducerThread, ProducerProcess
from procol.queue.threads import CallableRequests


def produce(request):
    #print 'Received', request
    #print 'Sending Back', request
    return request


def _test_queue(requests):
    assert (1, 2) == requests.execute((1, 2))
    result = requests.execute((3, 4))
    assert (3, 4) == result
    assert (5, 6) == requests.execute((5, 6))

    requests.close()


def _start_requests(request_class):
    requests = ProducerThread(request_class, producer=produce)
    requests.start()
    return requests


def _test_process_queue(request_class):
    requests = ProducerProcess(request_class, producer=produce)
    requests.start()
    _test_queue(requests)


def _test_thread_queue(request_class):
    requests = _start_requests(request_class)
    _test_queue(requests)


def _test_thread_pool():
    requests = ProducerThread(CallableRequests, producer=lambda function: produce(function()))

    requests.start()

    assert (1, 2) == requests.execute(lambda: (1, 2))
    result = requests.execute(lambda: (3, 4))
    assert (3, 4) == result
    assert (5, 6) == requests.execute(lambda: (5, 6))
    requests.close()


def _remote_manager_queue():
    queue = ProducerThread(ipc.ProducerConsumer, producer=produce)

    queue_manager = queue_manager_process(queue)
    return queue_manager


def _test_zero_mq():
    requests = _start_requests(zero_mq.Producer)
    _test_queue(zero_mq.Consumer())
    requests.close()


def main():
    _test_zero_mq()
    _test_process_queue(ipc.ProducerConsumer)
    _test_queue(_remote_manager_queue())

    _test_thread_queue(threads.ProducerConsumer)
    _test_thread_pool()

if __name__ == '__main__':
    main()