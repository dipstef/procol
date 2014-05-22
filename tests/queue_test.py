from procol.queue.remote_manager import queue_manager_process
from procol.queue import intra_processes, inter_process, ProducerConsumerThread, ProducerConsumerProcess
from procol.queue.inter_process import CallableRequests
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

    requests.close()


def _test_process_queue(request_class):
    requests = ProducerConsumerProcess(request_class)
    requests.produce(produce_fun=produce)
    _test_queue(requests)


def _test_thread_queue(request_class):
    requests = ProducerConsumerThread(request_class)

    requests.produce(produce_fun=produce)

    _test_queue(requests)


def _test_thread_pool():
    requests = ProducerConsumerThread(CallableRequests)

    requests.produce(lambda function: produce(function()))

    assert (1, 2) == requests.execute(lambda: (1, 2))
    result = requests.execute(lambda: (3, 4))
    assert (3, 4) == result
    assert (5, 6) == requests.execute(lambda: (5, 6))
    requests.close()


def _remote_manager_queue():
    queue = ProducerConsumerThread(intra_processes.ProducerConsumer)
    queue.produce(produce_fun=produce)

    queue_manager = queue_manager_process(queue)
    return queue_manager


def main():
    _test_process_queue(ProducerConsumerZeroMq)
    _test_process_queue(intra_processes.ProducerConsumer)
    _test_queue(_remote_manager_queue())

    _test_thread_queue(inter_process.ProducerConsumer)
    _test_thread_pool()

if __name__ == '__main__':
    main()