from Queue import Queue
import threading

from funlib import FunctionCall

from . import ProducerConsumerQueue, ProducerConsumer as ProducerConsumerBase, ProducerConsumerRun, ProducerQueue


class ThreadProducerQueue(ProducerQueue):
    def __init__(self):
        super(ThreadProducerQueue, self).__init__(Queue)

    def _result_produced(self, result):
        self._queue.task_done()

    def _finalize(self):
        #The interrupt signal
        self._queue.task_done()
        self._queue.join()


class ProducerConsumerThreadQueue(ProducerConsumerQueue):
    def __init__(self):
        super(ProducerConsumerThreadQueue, self).__init__(Queue)

    def _producer(self, queue_class):
        return ThreadProducerQueue()

    def _result_produced(self, result):
        super(ProducerConsumerThreadQueue, self)._result_produced(result)
        self._results.task_done()

    def _consumer_close(self):
        self._results.join()


#uses futures instead
class ThreadCallableRequests(ProducerConsumerBase):

    def __init__(self):
        super(ThreadCallableRequests, self).__init__(ThreadProducerQueue())

    def execute(self, request):
        request = ThreadFuture(request)
        self._producer.send(request)
        return request.result

    def _result_produced(self, result):
        super(ThreadCallableRequests, self)._result_produced(result)


ProducerConsumer = ProducerConsumerThreadQueue


class ThreadFuture(FunctionCall):

    def __init__(self, function):
        super(ThreadFuture, self).__init__(function)
        self._queue = Queue(1)

    def _call_fun(self, *args, **kwargs):
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