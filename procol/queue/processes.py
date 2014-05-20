import multiprocessing

from . import ProducerConsumerQueue, ProducerConsumerRun


class ProducerConsumer(ProducerConsumerQueue):

    def __init__(self):
        super(ProducerConsumer, self).__init__(multiprocessing.Queue)


class ProducerConsumerProcess(ProducerConsumerRun):

    def __init__(self, producer_consumer, producer_fun):
        super(ProducerConsumerProcess, self).__init__(multiprocessing.Process, producer_consumer, producer_fun)