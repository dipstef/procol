from multiprocessing import Process
import time

from procol.queue import zero_mq


def _sleep(j):
    time.sleep(j)
    return j


#producer = ProducerThread(producer=_sleep)
producer = zero_mq.ProducerProcess(producer=_sleep)
producer.start()


def _execute(j):
    result = producer.execute(j)
    print 'Received: ', result


processes = [Process(target=_execute, args=(i, )) for i in range(5)]
for process in processes:
    process.start()

for process in reversed(processes):
    process.join()

