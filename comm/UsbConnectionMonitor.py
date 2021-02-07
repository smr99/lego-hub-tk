from comm.SerialConnection import SerialConnection
import logging
import select

import pyudev
import serial
from serial.tools import list_ports

from comm.ConnectionMonitor import ConnectionMonitor

logger = logging.getLogger(__name__)


def is_lego_id(vid, pid):
    """Determine if a LEGO Hub by checking the vendor id and product id."""
    return vid == 1684 and pid == 16

def connected_comports():
    return [p for p in serial.tools.list_ports.comports() if is_lego_id(p.vid, p.pid)]

def is_lego_device(dev):
    props = dev.properties
    return props.get('ID_BUS') == 'usb' and props.get('SUBSYSTEM') == 'tty' and is_lego_id(int(props.get('ID_VENDOR_ID'), 16), int(props.get('ID_MODEL_ID'), 16))


class UsbConnectionMonitor(ConnectionMonitor):
    """Monitor the USB bus for add/removal of specified ports.

    Call method start() to initiate USB monitoring.    
    This version has hard-coded port selection criteria.
    The selected set of ports is available using method ports(),
    and, when changed, event ports_changed is raised.
    """
    def __init__(self):
        super(UsbConnectionMonitor, self).__init__("USB", self._thread_work)
        self._devname = None

    def is_online(self):
        return self._devname != None

    def reset(self):
        self._devname = None

    def _initial_scan(self):
        devices = connected_comports()
        if len(devices) == 0: return
        if len(devices) > 1:
            logger.warn('Multiple candidate devices, using the first: %s', ",".join(devices))
        self._add_port(devices[0].device)

    def _add_port(self, devname):
        if self._devname == devname: return
        if self._devname != None:
            logger.warn('will not overwrite existing port %s, ignoring add of port %s', self._devname, devname)
            return
        self._devname = devname
        ser = SerialConnection(devname)
        self.notify_change(ser)

    def _remove_port(self, devname):
        if self._devname != devname: return
        self._devname = None
        self.notify_change(None)        

    def _thread_work(self):
        """Monitor devices added/removed on the USB bus."""

        self._initial_scan()

        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.start()
        monitor.filter_by('tty')

        epoll = select.epoll()
        epoll.register(monitor.fileno(), select.POLLIN)

        while self.is_scan_active:
            try:
                events = epoll.poll()
            except InterruptedError:
                continue
            for fileno, _ in events:
                if fileno == monitor.fileno():
                    usb_dev = monitor.poll()
                    is_lego = is_lego_device(usb_dev)
                    logger.info('autoconnect: device %s (is_lego = %s), action: %s', usb_dev.device_node, is_lego, usb_dev.action)
                    if not is_lego_device(usb_dev): continue
                    if usb_dev.action == 'add':
                        self._add_port(usb_dev.properties['DEVNAME'])
                    elif usb_dev.action == 'remove':
                        self._remove_port(usb_dev.properties['DEVNAME'])
