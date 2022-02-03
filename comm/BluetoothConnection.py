import logging
from comm.Connection import Connection
import threading
import select
import socket


logger = logging.getLogger(__name__)

LINE_ENCODING = 'utf-8'
CR = 13 # Carriage Return

class BluetoothConnection(Connection):
    """Bluetooth RFCOMM-based communication with lego hub.
    """

    def __init__(self, address, port):
        """Create a connection to specified address.

        The connection is created in closed state.
        """

        super().__init__()
        self._socket = None
        self.address = address
        self.port = port

        self._opencloselock = threading.Lock()

    @property
    def name(self): return self.address

    def open(self):
        logger.debug('open socket to %s port %s', self.address, self.port)
        self._opencloselock.acquire()
        try:
            s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            s.connect((self.address, self.port))
            s.setblocking(False)
            self._socket = s
            self._start_monitor_loop()
        finally:
            self._opencloselock.release()

    def close(self):
        self._is_monitor_loop_active = False

        logger.debug('closing socket to %s', self.address)
        self._opencloselock.acquire()
        try:
            if self._socket.fileno() < 0:
                logger.warn('ignore request to close already-closed socket')
                return
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except Exception as ex:
                logger.exception('socket shutdown exception: %s', ex)
            self._socket.close()
        finally:
            self._opencloselock.release()

    def write(self, line : bytearray):
        """Send a line of text to the hub.  A CR will be appended before sending."""

        logger.debug('SEND: %s', line)
        data = (line + '\r').encode(LINE_ENCODING)
        written = self._socket.send(data)
        if written != len(data):
            logger.warn('wrote %d of %d bytes for line "%s"', written, len(data), line)

    def _start_monitor_loop(self):
        self._is_monitor_loop_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, name='BluetoothSocketRead')
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def _monitor_loop(self):
        try:
            logger.info('begin monitoring loop on device %s', self.address)
            
            lines_to_log = 10
            buffer = bytearray()
            inputs = [self._socket]
            while self._is_monitor_loop_active and self._socket.fileno() >= 0:
                readable, writable, exceptional = select.select(inputs, [], inputs)
                if exceptional:
                    logger.error('exception reading socket')
                    break
                if not readable:
                    continue
                buffer = buffer + self._socket.recv(1024)
                pos = buffer.find(CR)
                if pos >= 0:
                    line = buffer[:pos].decode(LINE_ENCODING)
                    buffer = buffer[pos+1:]
                    self.events.line_received(line)
                    if lines_to_log > 0:
                        logger.debug('RECV: %s', line)
                        lines_to_log -= 1
        except Exception as ex:
            logger.exception('monitor loop exception: %s', ex)

        logger.info('end monitoring loop')
        self.close()
