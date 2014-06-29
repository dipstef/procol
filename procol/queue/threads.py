from Queue import Queue

from funlib import FunctionCall

from . import ProducerConsumerQueue, ProducerConsumer as ProducerConsumerBase, ProducerQueue, \
    ProducerThread as RunInThread


class ThreadProducerQueue(ProducerQueue):
    def __init__(self):
        super(ThreadProducerQueue, self).__init__(Queue)

    def _result_produced(self, result):
        self._queue.task_done()

    def _finalize(self):
        #The interrupt signal
        self._queue.task_done()
        self._queue.join()


class ProducerConsumer(ProducerConsumerQueue):
    def __init__(self):
        super(ProducerConsumer, self).__init__(Queue)

    def _producer(self, queue_class):
        return ThreadProducerQueue()

    def _result_produced(self, result):
        super(ProducerConsumer, self)._result_produced(result)
        self._results.task_done()

    def _consumer_close(self):
        self._results.join()


#uses futures instead
class CallableRequests(ProducerConsumerBase):

    def __init__(self):
        super(CallableRequests, self).__init__(ThreadProducerQueue())

    def execute(self, request):
        request = InProcessFuture(request)
        self._producer.send(request)
        return request.result

    def _result_produced(self, result):
        super(CallableRequests, self)._result_produced(result)


class InProcessFuture(FunctionCall):

    def __init__(self, function):
        super(InProcessFuture, self).__init__(function)
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


class ProducerThread(RunInThread):
    def __init__(self, producer):
        super(ProducerThread, self).__init__(ProducerConsumer, producer)


class CallableRequestsThread(RunInThread):

    def __init__(self, producer):
        super(CallableRequestsThread, self).__init__(CallableRequests, producer)

    def execute(self, request):
        return self._producer_consumer.execute(request)