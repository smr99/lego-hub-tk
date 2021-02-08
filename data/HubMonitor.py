import base64
import datetime
import json
import logging
from enum import Enum
from queue import Queue

from comm.HubClient import ConnectionState
from comm.MultiplexedConnectionMonitor import MultiplexedConnectionMonitor
from comm.NullConnection import NullConnection
from events import Events
from utils.LockedCounter import LockedCounter

from data.HubStatus import HubStatus

logger = logging.getLogger(__name__)

LINE_ENCODING = 'utf-8'


class HubMonitor(object):
    def __init__(self, hub_client) -> None:
        self._client = hub_client
        self._status = HubStatus()

        hub_client.events.telemetry_update += self._on_telemetry_update

        self.events = Events(('console_print'))
        """Event triggered by user program on hub calling print()"""


    @property
    def status(self): return self._status

    @property
    def connection_device(self): return self._client.connection.name

    @property
    def connection_state(self): return self._client.state

    def _on_telemetry_update(self, timestamp, message):
        if 'm' in message:
            msgtype = message['m']
            if msgtype == 0:
                self._status.set_status0(message['p'])
                return
            elif msgtype == 2:
                self._status.set_status2(message['p'])
                return
            elif msgtype == 3:
                (button_id, millis) = message['p']
                if millis == 0:
                    logger.info('Button %s down', button_id)
                else:
                    logger.info('Button %s up after %d milliseconds', button_id, millis)
                return
            elif msgtype == 4:
                self._status.motion_sensor.record_event(timestamp, message['p'])
                return
            elif msgtype == 12:
                (program_id, is_running) = message['p']
                logger.info('Program ID %s changed run state to %s', program_id, is_running)
                return
            elif msgtype == 'userProgram.print':
                output = base64.b64decode(message['p']['value']).decode(LINE_ENCODING)
                logger.info('Program output: %s', output.strip())
                self.events.console_print(output)
                return

        logger.warn('unhandled message: %s', message)
