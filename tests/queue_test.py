from procol.queue import queue_process
from procol.queue.zero_mq import ProducerConsumerZeroMq


def produce(request):
        print 'Received: ', request
        print 'Sending back: ', request
        return request

def main():
    requests = ProducerConsumerZeroMq()
    requests = queue_process.ProducerConsumer()

    queue_process.ProducerConsumerProcess(requests, produce)

    assert (1, 2) == requests.execute((1, 2))
    assert (3, 4) == requests.execute((3, 4))
    assert (5, 6) == requests.execute((5, 6))

    #print 'Joining Thread'
    #producer_thread.join()

if __name__ == '__main__':
    main()