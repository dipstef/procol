from contextlib import contextmanager, closing

import zmq

from . import Producer, ProducerConsumer


class ProducerZeroMq(Producer):

    def __init__(self, host='127.0.0.1', port=5557):
        super(ProducerZeroMq, self).__init__()
        self._context = zmq.Context()
        self._address = 'tcp://{}:{}'.format(host, str(port))
        self._socket = None

    def _init(self):
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(self._address)

    def _send_request(self, request):
        with self.connect() as producer:
            producer.send_pyobj(request)

    @contextmanager
    def connect(self):
        with closing(self._context.socket(zmq.REQ)) as socket:
            socket.connect(self._address)
            yield socket

    def _result_produced(self, result):
        self._socket.send_pyobj(result)

    def _get_request(self):
        if self._socket:
            request = self._socket.recv_pyobj()
            return request

    def _finalize(self):
        self._socket.close()


class ProducerConsumerZeroMq(ProducerConsumer):
    def __init__(self, host='127.0.0.1', port=5557):
        super(ProducerConsumerZeroMq, self).__init__(ProducerZeroMq(host, port))
        self._address = 'tcp://{}:{}'.format(host, port)

        self._context = zmq.Context()

    def execute(self, request):
        with self._producer.connect() as producer:
            producer.send_pyobj(request)
            result = producer.recv_pyobj()
            return result