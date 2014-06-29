from contextlib import contextmanager, closing
from multiprocessing import Process, Lock
from threading import Thread

import zmq

from . import Producer as BaseProducer, ProducerRun as BaseProducerRun

_context = zmq.Context()


class Producer(BaseProducer):

    def __init__(self, host='127.0.0.1', port=5557):
        super(Producer, self).__init__()
        self._address = 'tcp://{}:{}'.format(host, str(port))
        self._socket = None

    def _init(self):
        self._socket = _context.socket(zmq.REP)
        self._socket.bind(self._address)

    def _result_produced(self, result):
        self._socket.send_pyobj(result)

    def _get_request(self):
        if self._socket:
            request = self._socket.recv_pyobj()
            return request

    def _finalize(self):
        print 'Closing Socket'
        self._socket.close()
        print 'Closed'


class Consumer(object):
    def __init__(self, host='127.0.0.1', port=5557):
        self._address = 'tcp://{}:{}'.format(host, port)
        self._lock = Lock()

    def execute(self, request):
        with self._connect_to_producer() as producer:
            producer.send_pyobj(request)
            result = producer.recv_pyobj()
            return result

    @contextmanager
    def _connect_to_producer(self):
        with closing(_context.socket(zmq.REQ)) as socket:
            socket.connect(self._address)
            yield socket

    def close(self):
        pass


class ProducerRun(BaseProducerRun):

    def __init__(self, producer, host='127.0.0.1', port=5557):
        super(ProducerRun, self).__init__(Producer(host, port), producer)
        self._address = (host, port)

    def execute(self, request):
        consumer = Consumer(*self._address)
        completed, result = consumer.execute(request)
        if not completed:
            raise result
        return result


class ProducerThread(ProducerRun):
    __concurrent__ = Thread


class ProducerProcess(ProducerRun):
    __concurrent__ = Process