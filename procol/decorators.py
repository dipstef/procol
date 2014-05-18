import multiprocessing
import threading


def thread_run(fun):
    def run(*args, **kwargs):
        t = threading.Thread(target=fun, args=args, kwargs=kwargs)
        t.start()

    return run


def process_run(fun):
    def run(*args, **kwargs):
        t = multiprocessing.Process(target=fun, args=args, kwargs=kwargs)
        t.start()

    return run