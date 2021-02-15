from abc import ABC, abstractmethod
import csv

class HubLogger(ABC):
    """Logs telemetry data from the LEGO Hub.
    """

    def __init__(self) -> None:
        self._csv_file = None
        self._csv_writer = None

    @abstractmethod
    def program_runstatus_update(self, timestamp, program_id, is_running):
        """Called when program's run status has changed."""
        pass

    @abstractmethod
    def telemetry_update(self, timestamp, message, hubstatus):
        """Called after hub status has been updated by the incoming message."""
        pass

    @property
    def is_logging(self):
        return self._csv_writer is not None

    def open_log_file(self, filename):
        self._csv_file = open(filename, 'a', newline='')
        self._csv_writer = csv.writer(self._csv_file, quoting=csv.QUOTE_MINIMAL)

    def close_log_file(self):
        if self._csv_writer:
            self._csv_file.close()
            self._csv_writer = None

    def writerow(self, row):
        if self.is_logging:
            self._csv_writer.writerow(row)

