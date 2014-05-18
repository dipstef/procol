from contextlib import contextmanager, closing

import zmq

from . import Producer, ProducerConsumer


class ProducerZeroMq(Producer):

    def __init__(self, host='127.0.0.1', port=5557):
        super(ProducerZeroMq, self).__init__()
        self._context = zmq.Context()
        self._address = 'tcp://{}:{}'.format(host, str(port))
        self._started = False

    def _init(self):
        self._producer = self._context.socket(zmq.REP)
        self._producer.bind(self._address)
        self._started = True

    def _send_request(self, request):
        if self._started:
            with self.connect() as producer:
                producer.send_pyobj(request)

    @contextmanager
    def connect(self):
        with closing(self._context.socket(zmq.REQ)) as producer:
            producer.connect(self._address)
            yield producer

    def add_result(self, result):
        self._producer.send_pyobj(result)

    def _get_request(self):
        request = self._producer.recv_pyobj()
        return request

    def _finalize(self):
        print 'Finaliz'
        self._producer.close()


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

    def add_result(self, result):
        self._producer.add_result(result)