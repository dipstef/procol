from contextlib import closing
from threading import Thread, Event

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
            socket.send_pyobj(produce(i))

        socket.close()

    def close(self):
        self._closed.set()
        context = zmq.Context()
        with closing(context.socket(zmq.REQ)) as socket:
            socket.connect(self._address)
            socket.send_pyobj(self._close_msg)


def produce(i):
    print_line('Performing: ', i)
    #time.sleep(i)
    return i


class Consumer(object):
    def __init__(self, port=5557):
        context = zmq.Context()

        address = 'tcp://{}:{}'.format('127.0.0.1', port)
        self._socket = context.socket(zmq.REQ)
        self._socket.connect(address)

    def send(self, i):
        self._socket.send_pyobj(i)
        result = self._socket.recv_pyobj()
        return result

    def close(self):
        self._socket.close()


def request(i):
    print_line('Requesting', i)

    consumer = Consumer()
    j = consumer.send(i)
    print_line('Received', j)


def main():
    worker = Worker()
    worker.start()

    threads = []
    for i in range(1, 10):
        t = Thread(target=request, args=(i, ))
        threads.append(t)
        t.start()

    [t.join() for t in threads]
    worker.close()


if __name__ == '__main__':
    main()