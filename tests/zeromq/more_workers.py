from contextlib import closing
from threading import Thread, Event
import time

import zmq

from procol.console import print_line


class Worker(Thread):
    def __init__(self, port=5557, local=False):
        self._address = 'tcp://{}:{}'.format('127.0.0.1' if local else '0.0.0.0', port)
        self._closed = Event()
        super(Worker, self).__init__(target=self._serve)
        self._close_msg = 'CLOSE'

    def _serve(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)

        socket.bind(self._address)

        while not self._closed.is_set():
            i = socket.recv_pyobj()
            if self._closed.is_set() and i == self._close_msg:
                break
            socket.send_pyobj(produce(self._address, i))

        socket.close()

    def close(self):
        self._closed.set()
        context = zmq.Context()
        with closing(context.socket(zmq.REQ)) as socket:
            socket.connect(self._address)
            socket.send_pyobj(self._close_msg)


def produce(address, i):
    print_line(address, ' Performing: ', i)
    time.sleep(1)
    return str(i) + ' from ' + address


class Consumer(object):
    def __init__(self, ports):
        assert ports
        self._addresses = ['tcp://{}:{}'.format('127.0.0.1', port) for port in ports]
        context = zmq.Context()

        self._socket = context.socket(zmq.REQ)
        for address in self._addresses:
            self._socket.connect(address)

    def send(self, i):
        self._socket.send_pyobj(i)
        result = self._socket.recv_pyobj()
        return result

    def close(self):
        self._socket.close()


def request(consumer, i):
    print_line('Requesting', i)

    j = consumer.send(i)
    print_line('Received', j)


def main():
    ports = range(5557, 5561)
    workers = [Worker(port) for port in ports]
    [worker.start() for worker in workers]

    consumer = Consumer(ports)

    for i in range(1, 10):
        request(consumer, i)

    [worker.close() for worker in workers]


if __name__ == '__main__':
    main()