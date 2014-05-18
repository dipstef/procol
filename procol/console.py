from __future__ import print_function
import sys
import traceback
from multiprocessing import Lock

print_lock = Lock()


def print_line(*msg):
    with print_lock:
        print(*msg)
        sys.stdout.flush()


def print_err(*msg):
    with print_lock:
        print(*msg, file=sys.stderr)
        sys.stderr.flush()


def print_err_trace(*msg):
    print_err(' '.join(('%s' % m for m in msg)), ':', traceback.format_exc())