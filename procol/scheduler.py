import atexit
from threading import Timer, Event

from dated.timedelta import to_seconds


class Repeater(object):

    def __init__(self, fun, after, every=None):
        self._seconds_repeat = to_seconds(every or after)
        self._fun = fun
        self._stopped = Event()

        self._timer = self._schedule(to_seconds(after))
        atexit.register(self._exit)

    def start(self):
        self._timer.start()

    def _repeat(self):
        self._fun()
        if not self._stopped.is_set():
            self._timer = self._schedule(self._seconds_repeat)
            self._timer.start()

    def _schedule(self, secs):
        timer = Timer(secs, self._repeat)
        timer.daemon = True
        return timer

    def _exit(self):
        self._stopped.set()
        self._timer.join()

    def cancel(self):
        self._stopped.set()
        self._timer.cancel()


class Scheduler(object):

    def __init__(self, fun):
        self._fun = fun

    def __call__(self, after, repeat=False):
        timer = Repeater(self._fun, after) if repeat else Timer(to_seconds(after), self._fun)
        timer.start()
        return timer


def schedule(fun, after, repeat=False):
    scheduler = Scheduler(fun)

    return scheduler(after, repeat=repeat)


def repeat(fun, every, after=None):
    repeater = Repeater(fun, after=after or every, every=every)
    repeater.start()
    return repeater