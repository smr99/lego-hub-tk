from abc import ABC, abstractmethod
import logging
import threading

from events import Events

logger = logging.getLogger(__name__)


class ConnectionMonitor(ABC):
    """Monitor hardware for connection to device.

    Arguments:
        name : str
            user-visible name of the hardware type being monitored
        thread_work : function
            function that scans for the hardware; invoked on its own thread
            function must call property is_scan_active periodically

    Call method start() to initiate the monitoring.
    While monitoring, the event connection_changed is raised.

    Call method stop() to discontinue monitoring.
    """
    def __init__(self, name, thread_work):
        self._connect_thread = None
        self._is_scan_active = False

        self._name = name
        self._connection = None

        self._thread_work = thread_work
        self.events = Events(('connection_changed'))
        """Event indicates change in connection availability.
        
        Event arguments:
            connection object if connection available, else None
    """

    @property
    def name(self):
        """User-visible name of the hardware being monitored.  
        
        This will typically name the type of hardware being monitored; e.g. USB or BlueTooth."""
        return self._name

    @property
    def connection(self):
        """Currently-available connection; or None if no connection available.

        This is the value sent in the last connection_changed event.
        """
        return self._connection

    def notify_change(self, connection):
        """Raise connection_changed event.

        connection: a connection object (if connection available) or None if connection removed.
        """
        self._connection = connection
        self.events.connection_changed(connection)

    @property
    def is_scan_active(self):
        return self._is_scan_active

    def start(self):
        """Start hardware monitoring.
        """
        self._is_scan_active = True
        self._connect_thread = threading.Thread(target=self._scan_loop, name='ConnectionMonitor-' + self.name)
        self._connect_thread.daemon = True
        self._connect_thread.start()

    def stop(self):
        """Stop hardware monitoring.
        """
        self._is_scan_active = False

    def _scan_loop(self):
        logger.info('Starting %s autoconnect detection loop', self.name)
        try:
            self._thread_work()
        except Exception as ex:
            logger.exception('autoconnect loop exception: %s', ex)
        self._is_scan_active = False
        logger.info('End %s autoconnect detection loop', self.name)
