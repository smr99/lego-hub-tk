from data.BasicHubLogger import BasicHubLogger
import os

class ProgramHubLogger(BasicHubLogger):
    """Basic logger that writes a timestamped row of status information on each telemetry update.

    Logging is written to a separate file for each program, using the program ID as the filename.
    Logging is automatically initiated and stopped when the program starts and stops.
    """

    def __init__(self, logdir) -> None:
        """Construct logger, specifying the log directory.  

        The log files will be created as {program-id}.csv within the log directory.
        The directory will be created if necessary.  Log files are opened in append mode.
        """
        super().__init__()
        os.makedirs(logdir, exist_ok=True)
        self._logdir = logdir

    def program_runstatus_update(self, timestamp, program_id, is_running):
        self.close_log_file()
        if is_running:
            self.open_log_file(self._logdir + "/" + program_id + ".csv")
