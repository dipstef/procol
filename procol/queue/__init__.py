import atexit
import thread
from threading import Thread
from multiprocessing import Process, Event, Lock


class ProducerRequests(object):

    def __init__(self):
        self._closed = Event()

        atexit.register(self.close)

    def requests(self):
        self._init()

        for request in self._iterate_requests():
            yield request

        self._finalize()

    def _iterate_requests(self):
        while True:
            try:
                request = self._get_request()
                if isinstance(request, _Interrupt):
                    break
                yield request
            except (KeyboardInterrupt, SystemExit):
                self.close()
                thread.interrupt_main()

    def _init(self):
        pass

    def _finalize(self):
        pass

    def _get_request(self):
        raise NotImplementedError

    def close(self):
        if self._active_queue():
            self._closed.set()
            self._interrupt()

    def _active_queue(self):
        return not self._closed.is_set()

    def __iter__(self):
        return self.requests()

    def _interrupt(self):
        pass


class Producer(ProducerRequests):

    def requests(self, on_result=None):
        requests = super(Producer, self).requests()
        for request in requests:
            result = (yield request)

            self._result_produced(result)
            if on_result:
                on_result(result)
            yield

    def _result_produced(self, result):
        pass


class ProducerQueue(Producer):

    def __init__(self, queue_class):
        super(ProducerQueue, self).__init__()
        self._queue = queue_class(1)

    def send(self, request):
        if not self._active_queue():
            raise RequestsClosed('Queue already closed can not perform: %s' % request)
        try:
            return self._send_request(request)
        except (KeyboardInterrupt, SystemExit):
            self.close()
            raise

    def _send_request(self, request):
        return self._queue.put(request)

    def _get_request(self):
        request = self._queue.get()
        return request

    def _finalize(self):
        self._queue.close()

    def _interrupt(self):
        self._send_request(_Interrupt())


class ProducerConsumer(object):
    def __init__(self, producer):
        self._producer = producer

    def execute(self, request):
        raise NotImplementedError

    def close(self):
        self._producer_close()
        self._consumer_close()

    def requests(self):
        return self._producer.requests(on_result=self._result_produced)

    def _result_produced(self, result):
        pass

    def _producer_close(self):
        self._producer.close()

    def _consumer_close(self):
        pass


class ProducerConsumerQueue(ProducerConsumer):
    def __init__(self, queue_class):
        super(ProducerConsumerQueue, self).__init__(self._producer(queue_class))
        self._execute_lock = Lock()
        self._results = queue_class(1)

    def _producer(self, queue_class):
        return ProducerQueue(queue_class)

    def execute(self, request):
        with self._execute_lock:
            self._producer.send(request)
            return self._get_result()

    def _result_produced(self, result):
        self._results.put(result)

    def _get_result(self):
        return self._results.get()

    def _consumer_close(self):
        self._results.close()


class _Interrupt(object):
    pass


class RequestsClosed(Exception):
    def __init__(self, *args, **kwargs):
        super(RequestsClosed, self).__init__(*args, **kwargs)


class ProducerRun(object):

    def __init__(self, producer_consumer, producer):
        self._producer_consumer = producer_consumer
        self._producer = producer
        self._running = False
        self._lock = Lock()

    def start(self):
        with self._lock:
            if not self._running:
                concurrent = self.__concurrent__(target=self._produce_requests, args=(self._producer, ))

                concurrent.daemon = True
                concurrent.start()
                self._running = True
            else:
                raise RuntimeError('Already running')

    def __getattr__(self, item):
        return getattr(self._producer_consumer, item)

    def _produce_requests(self, produce):
        requests = self._producer_consumer.requests()
        for request in requests:
            result = produce(request)
            requests.send(result)
            #print request
        self._done_requests()

    def _done_requests(self):
        pass

    def close(self):
        self._producer_consumer.close()


class ProducerConsumerRun(ProducerRun):

    def __init__(self, producer_consumer_class, producer):
        super(ProducerConsumerRun, self).__init__(producer_consumer_class(), producer)

    def execute(self, request):
        return self._producer_consumer.execute(request)


class ProducerThread(ProducerConsumerRun):
    __concurrent__ = Thread


class ProducerProcess(ProducerConsumerRun):
    __concurrent__ = Process





