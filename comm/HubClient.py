import comm.ConnectionFactory
from comm.Connection import Connection
import appdirs
import cfg_load
import base64
from utils.LockedCounter import LockedCounter
from comm.NullConnection import NullConnection
import datetime
import json
import logging
import os, os.path
from events import Events
from queue import Queue
from enum import Enum


logger = logging.getLogger(__name__)

config_file = os.path.join(appdirs.user_config_dir('lego-hub-tk'), 'lego_hub.yaml')
if os.path.exists(config_file):
    logger.info('Loading configuration from %s', config_file)
    config = cfg_load.load(config_file)
else:
    # dummy config
    logger.warn('Configuration file does not exist: %s', config_file)
    config = {}

LINE_ENCODING = 'utf-8'


class ConnectionState(Enum):
    DISCONNECTED = 0
    """Initial state; no connection to hub"""
    CONNECTING = 1
    """Attempting to connect to the hub"""
    TELEMETRY = 2
    """Hub is sending its status regularly"""
    DISCONNECTING = 3




class HubClient(object):
    """HubClient provides low-level line-oriented interface to the LEGO Hub
    via a serial connection.
    
    """

    def __init__(self, cm = None):
        self._response_queue = Queue()
        self.events = Events(('connection_state_changed', 'telemetry_update'))
        self._id_counter = LockedCounter(1000)

        self.state = ConnectionState.DISCONNECTED
        """state of the hub connection"""

        if cm is None:
            cm = comm.ConnectionFactory.make_connection_monitor(config)

        self._connection_monitor = cm
        self._connection_monitor.events.connection_changed += self._connection_changed
        self._connection = NullConnection() # value managed by connection monitor

    @property
    def connection(self): return self._connection

    def _set_connection_state(self, newstate):
        oldstate = self.state
        self.state = newstate
        if oldstate == newstate: return
        logging.info('Connection state change %s --> %s', oldstate, newstate)
        self.events.connection_state_changed(oldstate, newstate)

    def start(self):
        """Start monitoring physical connections for LEGO Hub.
        """
        self._connection_monitor.start()

    def _connection_changed(self, conn : Connection):
        try:
            self._connection.events.line_received -= self._on_line_received
            self._connection.close()
            if conn is not None:
                logger.info('Connecting to hub using %s', conn.name)
                self._connection = conn
                self._connection.events.line_received += self._on_line_received
                self._set_connection_state(ConnectionState.CONNECTING)
                conn.open()
            else:
                logger.info('Hub disconnected')
                self._connection = NullConnection()
                self._set_connection_state(ConnectionState.DISCONNECTED)
        except Exception as ex:
            logger.exception('connection change failed: %s', ex)
            self._connection.events.line_received -= self._on_line_received
            self._connection = NullConnection()
            self._set_connection_state(ConnectionState.DISCONNECTED)

    def send_line(self, line):
        """Send one line of text to the hub.  

        Prerequisite: serial device should be connected.
        Input line is string, with no end-of-line character.
        """
        self._connection.write(line)

    def _gen_message_id(self):
        import string, random
        length = 4
        letters = string.ascii_letters + string.digits + '_'
        return ''.join(random.choice(letters) for _ in range(length))    

    def send_message(self, name:str, params = {}):
        """Send a message and return the response.
        """
        if self.state != ConnectionState.TELEMETRY:
            logger.warn('ignoring send request in state %s', self.state)
            return

        id = self._gen_message_id()
        msg = {'m':name, 'p': params, 'i': id}
        msg_string = json.dumps(msg)
        self.send_line(msg_string)
        while True:
            resp = self._response_queue.get()
            if resp['i'] == id: 
                if 'r' in resp: 
                    return resp['r']
                if 'e' in resp: 
                    error = json.loads(base64.b64decode(resp['e']).decode(LINE_ENCODING))
                else:
                    error = 'unrecognized response message: %s' % resp
                raise ConnectionError(error)
            else:
                logger.warn('ignored response: ', resp)
                
    def send_response(self, id: str, response = None):
        """Send a response.
        """
        if self.state != ConnectionState.TELEMETRY:
            logger.warn('ignoring send request in state %s', self.state)
            return

        msg = {'i': id, 'r': response}
        msg_string = json.dumps(msg)
        self.send_line(msg_string)

    def _on_line_received(self, line):
        state = self.state
        line = line.strip()
        if state == ConnectionState.CONNECTING: self._process_line_connecting(line)
        elif state == ConnectionState.TELEMETRY: self._process_line_telemetry(line)
        else:
            logger.warn('State %s, ignoring input: ', state, line)

    def _process_line_connecting(self, line):
        """Process data received during state CONNECTING."""
        if len(line) > 0 and line[0] == '{':
            self._set_connection_state(ConnectionState.TELEMETRY)
        else:
            logger.info('CONNECTING: %s', line)

    def _process_line_telemetry(self, line):
        begin = line.find('{')
        if begin >=0:
            try:
                message = json.loads(line[begin:])
                self.process_message(message)
            except json.JSONDecodeError:
                logger.warn('failed to decode JSON message: %s', line) 
        else:
            logger.info('received non-JSON: %s', line)

    def process_message(self, message):
        timestamp = datetime.datetime.now()
        if 'm' in message:
            self.events.telemetry_update(timestamp, message)
            return
        elif 'i' in message:
            self._response_queue.put(message)
            return

        logger.warn('unhandled message: %s', message)

    def get_storage_status(self):
        return self.send_message('get_storage_status')

    def program_execute(self, slot):
        return self.send_message('program_execute', {'slotid': slot}) 

    def program_terminate(self):
        return self.send_message('program_terminate')
