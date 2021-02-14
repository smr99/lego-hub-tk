from abc import ABC, abstractmethod
from events import Events

class Connection(ABC):
    """Abstractly, a Connection is a class that provides data communications with the LEGO Hub.
    """

    def __init__(self):

        self.events = Events(('line_received'))
        """Events raised by a Connection:

            line_recieved(line : bytearray) - provides raw text received from hub.
        """

    @property
    @abstractmethod
    def name(self):
        """User-visible name of the connection.  
        
        This will typically name a physical hardware device, e.g. /dev/ACM0."""
        pass

    @abstractmethod
    def open(self):
        """Open the connection for use.
        Failure will be signaled by an exception."""
        pass

    @abstractmethod
    def close(self):
        """Shut down the connection.  This object is not to be re-used."""
        pass

    @abstractmethod
    def write(self, line : bytearray):
        """Send a line of text to the hub.  A CR will be appended before sending."""
        pass
