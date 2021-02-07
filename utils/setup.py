import logging, logging.handlers
import os
import sys


def setup_logging(log_filename, console_level=logging.INFO, file_level=logging.DEBUG):
    """Configure console and file logging.
    """

    # See https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout/13733863#13733863

    logformat = '%(asctime)s %(levelname)s %(name)s %(message)s'

    # Change root logger level from WARNING (default) to NOTSET in order for all messages to be delegated.
    logging.getLogger().setLevel(logging.NOTSET)

    # Add stdout handler, with level INFO
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(console_level)
    console.setFormatter(logging.Formatter(logformat))
    logging.getLogger().addHandler(console)

    # Add file rotating handler, with level DEBUG
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    rotatingHandler = logging.handlers.TimedRotatingFileHandler(filename=log_filename, backupCount=5)
    rotatingHandler.setLevel(file_level)
    rotatingHandler.setFormatter(logging.Formatter(logformat))
    logging.getLogger().addHandler(rotatingHandler)

