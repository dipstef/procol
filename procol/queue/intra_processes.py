import multiprocessing

from . import ProducerConsumerQueue


class ProducerConsumer(ProducerConsumerQueue):

    def __init__(self):
        super(ProducerConsumer, self).__init__(multiprocessing.Queue)