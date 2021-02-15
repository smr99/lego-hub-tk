from data.HubStatus import HubStatus
from data.HubLogger import HubLogger
import os

class BasicHubLogger(HubLogger):
    """Basic logger that writes a timestamped row of status information on each telemetry update.

    Logging is started and stopped programatically.
    """

    def __init__(self) -> None:
        """Construct basic logger.  
        """
        super().__init__()

        self.get_row = BasicHubLogger.log_position
        """Method get_row can be set to a function that returns an iterable for a single row.
        The function will be provided parameters (timestamp, hubstatus), where hubstatus
        is an instance of class HubStatus, after having been updated by telemetry.
        """

    def start(self, logfile : str):
        if self.is_logging: self.stop()
        self.open_log_file(logfile)

    def stop(self):
        self.close_log_file()

    def program_runstatus_update(self, timestamp, program_id, is_running):
        pass

    def telemetry_update(self, timestamp, message, hubstatus : HubStatus):
        if not self.is_logging: return
        self.writerow(self.get_row(timestamp, hubstatus))

    def log_position(timestamp, hubstatus : HubStatus):
        (yaw, pitch, roll) = hubstatus.orientation()
        (x,y,z) = hubstatus.gyroscope()
        return [timestamp, x, y, z, yaw, pitch, roll]

