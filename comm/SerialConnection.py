import logging
import threading

import serial
from serial.serialutil import SerialException

from comm.Connection import Connection


logger = logging.getLogger(__name__)

LINE_ENCODING = 'utf-8'
CR = 13 # Carriage Return


class SerialConnection(Connection):
    """Serial port communication with the lego hub.
    """

    def __init__(self, port):
        """Create a connection.

        The port may optionally be specified.  Otherwise, set the port property.
        The connection is created in closed state.
        """
        super().__init__()
        self._serial = serial.Serial()
        self._serial.port = port

    @property
    def name(self):
        return self._serial.port

    def open(self):
        """Open the connection for use.
        """
        self._serial.open()
        self._start_monitor_loop()

    def close(self):
        """Shut down the connection."""
        self._serial.close()

    def write(self, line : bytearray):
        """Send a line of text to the hub.  A CR will be appended before sending."""
        logger.debug('SEND: %s', line)
        data = (line + '\r').encode(LINE_ENCODING)
        written = self._serial.write(data)
        if written != len(data):
            logger.warn('wrote %d of %d bytes for line "%s"', written, len(data), line)
        
    def _start_monitor_loop(self):
        self._monitor_thread = threading.Thread(target=self._monitor_loop, name='HubConnectionMonitor')
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def _monitor_loop(self):
        try:
            logger.info('begin monitoring loop on device %s', self.name)
            
            lines_to_log = 10
            buffer = bytearray()
            while self._serial.is_open:
                count = self._serial.in_waiting
                buffer = buffer + self._serial.read(count if count else 1)
                pos = buffer.find(CR)
                if pos >= 0:
                    line = buffer[:pos].decode(LINE_ENCODING)
                    buffer = buffer[pos+1:]
                    self.events.line_received(line)
                    if lines_to_log > 0:
                        logger.debug('RECV: %s', line)
                        lines_to_log -= 1
        except SerialException:
            pass # expected when the device disconnects or powers off
        except Exception as ex:
            logger.exception('monitor loop exception: %s', ex)
        finally:
            self.close()
        logger.info('end monitoring loop')

