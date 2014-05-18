from Queue import Queue as ThreadQueue
import threading

from . import ProducerConsumerQueue, ProducerConsumerRun


class ProducerConsumer(ProducerConsumerQueue):
    def __init__(self):
        super(ProducerConsumer, self).__init__(ThreadQueue)

    def execute(self, request):
        request = ThreadFuture(request)
        self._producer.send(request)
        return request.result


class ThreadFuture(object):
    def __init__(self, fun):
        self._fun = fun
        self._queue = ThreadQueue(1)

    def __call__(self, *args, **kwargs):
        completed, result = False, None
        try:
            result = self._fun(*args, **kwargs)
            completed = True

        except BaseException, e:
            result = e
        finally:
            self._queue.put((completed, result))

        return result

    @property
    def result(self):
        completed, result = self._queue.get()

        if not completed:
            raise result

        return result


class ProducerConsumerThread(ProducerConsumerRun):

    def __init__(self, producer_consumer, producer_fun):
        super(ProducerConsumerThread, self).__init__(threading.Thread, producer_consumer, producer_fun)