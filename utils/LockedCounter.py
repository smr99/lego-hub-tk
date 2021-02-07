import threading

class LockedCounter(object):
    """Thread-safe integer counter.  Can be used to generate unique IDs.
    """

    def __init__(self, initial = 1) -> None:
        self._next_id = initial
        self._lock = threading.Lock()

    def reset(self, value):
        """Set the next counter to specified value."""
        self._lock.acquire()
        try:
            self._next_id = value
        finally:
            self._lock.release()

    def next_value(self):
        """Obtain next counter value."""
        self._lock.acquire()
        try:
            id = self._next_id
            self._next_id += 1
        finally:
                self._lock.release()
        return id
