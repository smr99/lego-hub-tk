import logging

from comm.Connection import Connection

logger = logging.getLogger(__name__)


class NullConnection(Connection):

    @property
    def name(self): return "No connection"

    def open(self):
        pass

    def close(self):
        pass

    def write(self, line : bytearray):
        logger.warn("Ignoring write to null connection: %s", line)

