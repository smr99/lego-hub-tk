import threading
from events import Events


class SharedCache(object):
    """Thread-safe set used to cache shared objects.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._cache = set()
        self.events = Events(('cache_changed'))

    def contents(self):
        self._lock.acquire()
        cache = [o for o in self._cache]
        self._lock.release()
        return cache

    def add(self, obj):
        self._lock.acquire()
        self._cache.add(obj)
        cache = [o for o in self._cache]
        self._lock.release()
        self.events.cache_changed(self, cache)

    def add_many(self, objects):
        self._lock.acquire()
        for obj in objects:
            self._cache.add(obj)
        cache = [o for o in self._cache]
        self._lock.release()
        self.events.cache_changed(self, cache)

    def discard(self, obj):
        self._lock.acquire()
        self._cache.discard(obj)
        cache = [o for o in self._cache]
        self._lock.release()
        self.events.cache_changed(self, cache)
