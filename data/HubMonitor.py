import base64
import logging

from events import Events
from comm import HubClient
from data.HubStatus import HubStatus
from data.NullHubLogger import NullHubLogger

logger = logging.getLogger(__name__)

LINE_ENCODING = 'utf-8'


class HubMonitor(object):
    def __init__(self, hub_client: HubClient) -> None:
        self._client: HubClient = hub_client
        self._status = HubStatus()
        self._execution_status = (None, None)

        hub_client.events.telemetry_update += self._on_telemetry_update

        self.events = Events(('console_print'))
        """Event triggered by user program on hub calling print()"""

        self.logger = NullHubLogger()

    @property
    def status(self): return self._status

    @property
    def connection_device(self): return self._client.connection.name

    @property
    def connection_state(self): return self._client.state

    @property
    def execution_status(self): return self._execution_status

    def _on_telemetry_update(self, timestamp, message):
        message_recognized = True
        if 'm' in message:
            msgtype = message['m']
            if msgtype == 0:
                self._status.set_status0(message['p'])
                self.logger.telemetry_update(timestamp, message, self.status)
            elif msgtype == 1:
                # TODO handle m:1 (storage status)
                pass
            elif msgtype == 2:
                self._status.set_status2(message['p'])
                self.logger.telemetry_update(timestamp, message, self.status)
            elif msgtype == 3:
                (button_id, millis) = message['p']
                if millis == 0:
                    logger.info('Button %s down', button_id)
                else:
                    logger.info('Button %s up after %d milliseconds', button_id, millis)
            elif msgtype == 4:
                self._status.motion_sensor.record_event(timestamp, message['p'])
            elif msgtype == 12:
                (program_id, is_running) = message['p']
                logger.info('Program ID %s changed run state to %s', program_id, is_running)
                self._execution_status = (program_id, is_running)
                self.logger.program_runstatus_update(timestamp, program_id, is_running)
            elif msgtype == 'userProgram.print':
                output = base64.b64decode(message['p']['value']).decode(LINE_ENCODING)
                self._client.send_response(message['i'])
                logger.info('Program output: %s', output.strip())
                self._client.send_response(message['i'])
                self.events.console_print(output)
            elif msgtype == 'user_program_error':
                params = message['p']
                logger.info('Program error output: %s', params[0:3])
                err =  base64.b64decode(params[3]).decode(LINE_ENCODING)
                logger.info('Program error message: %s', err.strip())
                self.events.console_print("***ERROR\n" + err)
            elif msgtype == 'runtime_error':
                params = message['p']
                logger.info('Runtime error output: %s', params[0:3])
                err =  base64.b64decode(params[3]).decode(LINE_ENCODING)
                logger.info('Program error message: %s', err.strip())
                self.events.console_print("***ERROR (Runtime)\n" + err)
            else:
                message_recognized = False
        else:
            message_recognized = False

        if not message_recognized:
            logger.warn('unhandled message: %s', message)

            # TODO handle message types:
            # {'m': 7, 'p': 'zBAZ4zVlAjuemfPMBTr3'}  # stack started, 'p' is the vm id
            # {'m': 8, 'p': 'zBAZ4zVlAjuemfPMBTr3'}  # stack ended, 'p' is the vm id
