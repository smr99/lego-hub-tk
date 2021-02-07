import logging
import time

import bluetooth
from events import Events

from comm.BluetoothConnection import BluetoothConnection
from comm.ConnectionMonitor import ConnectionMonitor

logger = logging.getLogger(__name__)

# Bluetooth poll interval
poll_interval = 5


class BluetoothConnectionMonitor(ConnectionMonitor):
    """Monitor the Bluetooth device for add/removal of specified devices.

    Call method start() to initiate bluetooth monitoring.
    The selected set of ports is available using method ports(),
    and, when changed, event ports_changed is raised.
    """
    def __init__(self, target_address, port):
        super().__init__("Bluetooth", self._thread_work)
        
        self.is_online = False
        """Boolean value indicating whether target device is online."""

        self.target_address = target_address
        """Bluetooth address to scan for."""

        self.port = port
        """Bluetooth device port for RFCOMM"""

    def is_online(self):
        return self.is_online

    def reset(self):
        self.is_online = False

    def _set_scan_result(self, is_online):        
        if self.is_online == is_online: return
        self.is_online = is_online
        if is_online:
            conn = BluetoothConnection(self.target_address, self.port)
            self.notify_change(conn)
        else:
            self.notify_change(None)

    def _thread_work(self):
        if self.target_address is None:
            logger.warn('Not scanning: no BlueTooth address configured')
            return
        lookup_prev = None
        while self.is_scan_active:
            try:
                time.sleep(poll_interval)
                lookup = bluetooth.lookup_name(address = self.target_address)
                if lookup != lookup_prev:
                    logger.info('BlueTooth scan result: %s --> %s', lookup_prev, lookup)
                    self._set_scan_result(lookup is not None)
                    lookup_prev = lookup
            except Exception:
                logger.exception('failure in bluetooth scan loop')
