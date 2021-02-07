import logging
from comm.ConnectionMonitor import ConnectionMonitor

from events import Events

logger = logging.getLogger(__name__)


class DirectConnectionMonitor(ConnectionMonitor):
    """Null implementation of a ConnectionMonitor that provides access to one device only.

    When the scan is initiated, this device is "detected" and never removed thereafter.

    Arguments:
        connection : Connection
    """
    def __init__(self, connection):
        super().__init__(connection.name, self._scan_loop)
        self._connection = connection

    def _scan_loop(self):
        self.notify_change(self._connection)
