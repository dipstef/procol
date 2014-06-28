import multiprocessing

from . import ProducerConsumerQueue, ProducerThread as RunInThread, ProducerProcess as RunInProcess


class ProducerConsumer(ProducerConsumerQueue):

    def __init__(self):
        super(ProducerConsumer, self).__init__(multiprocessing.Queue)


class ProducerThread(RunInThread):
    def __init__(self, producer):
        super(ProducerThread, self).__init__(ProducerConsumer, producer)


class ProducerProcess(RunInProcess):
    def __init__(self, producer):
        super(ProducerProcess, self).__init__(ProducerConsumer, producer)