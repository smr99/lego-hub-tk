from comm.ConnectionMonitor import ConnectionMonitor
from comm.BluetoothConnectionMonitor import BluetoothConnectionMonitor
from comm.UsbConnectionMonitor import UsbConnectionMonitor
from comm.SerialConnection import SerialConnection
import logging
from serial.tools import list_ports

logger = logging.getLogger(__name__)


class MultiplexedConnectionMonitor(ConnectionMonitor):
    """Monitors both the USB bus and BlueTooth for connection to the hub.

    If both are available, the USB device is preferred.
    """
    def __init__(self, bt_address, bt_port):
        super().__init__('Multiplexed', None)
        self._usb_monitor = UsbConnectionMonitor()
        self._usb_monitor.events.connection_changed += self._on_usb_connection_changed
        self._bt_monitor = BluetoothConnectionMonitor(bt_address, bt_port)
        self._bt_monitor.events.connection_changed += self._on_bt_connection_changed

    def start(self):
        is_scan_active = True
        self._usb_monitor.start()
        self._bt_monitor.start()

    def stop(self):
        is_scan_active = False
        self._usb_monitor.stop()
        self._bt_monitor.stop()

    def _on_usb_connection_changed(self, conn):
        if conn == self.connection: return

        if conn is None:
            # fallback to BlueTooth, which may well also be None
            self.notify_change(self._bt_monitor.connection)
        else:
            # switch to USB
            self.notify_change(conn)

    def _on_bt_connection_changed(self, conn):
        if conn == self.connection: return

        # if currently using USB, ignore this update; else accept
        if self._usb_monitor.connection is None:
            self.notify_change(conn)
