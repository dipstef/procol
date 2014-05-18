from threading import Timer


def schedule_function(seconds, fun, daemon=False):
    timer = Timer(seconds, fun)
    timer.daemon = daemon
    timer.start()


def schedule_every(seconds, fun, daemon=True):

    def schedule_after():
        fun()
        schedule_function(seconds, schedule_after, daemon=daemon)

    schedule_function(seconds, schedule_after, daemon=daemon)