import atexit
import multiprocessing
import thread

from ..console import print_err


class Producer(object):

    def __init__(self):
        self._closed = multiprocessing.Event()

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
                print_err(self.__class__.__name__, 'Queue Exiting')
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
            self._send_request(_Interrupt())

    def _active_queue(self):
        return not self._closed.is_set()

    def send(self, request):
        if not self._active_queue():
            raise RequestsClosed('Queue already closed can not perform: %s' % request)
        try:
            return self._send_request(request)
        except (KeyboardInterrupt, SystemExit):
            self.close()
            raise

    def _send_request(self, request):
        raise NotImplementedError

    def __iter__(self):
        return self.requests()


class ProducerConsumer(object):
    def __init__(self, producer):
        self._producer = producer

    def execute(self, request):
        raise NotImplementedError

    def close(self):
        self._producer.close()
        self._consumer_close()

    def requests(self):
        return self._producer.requests()

    def _consumer_close(self):
        pass

    def __iter__(self):
        return self._producer.requests()


class ProducerQueue(Producer):

    def __init__(self, producer_queue):
        super(ProducerQueue, self).__init__()
        self._producer = producer_queue(1)

    def _send_request(self, request):
        return self._producer.put(request)

    def _get_request(self):
        request = self._producer.get()
        return request

    def _finalize(self):
        self._producer.close()


class ProducerConsumerQueue(ProducerConsumer):
    def __init__(self, queue_class):
        super(ProducerConsumerQueue, self).__init__(ProducerQueue(queue_class))
        self._execute_lock = multiprocessing.Lock()
        self._consumer = queue_class(1)

    def execute(self, request):
        with self._execute_lock:
            self._producer.send(request)
            return self._get_result()

    def _get_result(self):
        return self._consumer.get()

    def add_result(self, result):
        self._consumer.put(result)

    def _consumer_close(self):
        self._consumer.close()


class _Interrupt(object):
    pass


class RequestsClosed(Exception):
    def __init__(self, *args, **kwargs):
        super(RequestsClosed, self).__init__(*args, **kwargs)


class ProducerConsumerRun(object):

    def __init__(self, concurrent_class, producer_consumer, producer_fun):
        concurrent_class(target=_produce_results, args=(producer_consumer, producer_fun)).start()


def _produce_results(producer, process_request):
    for request in producer.requests():
        result = process_request(request)
        producer.add_result(result)