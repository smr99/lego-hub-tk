class TimeStampedData(object):
    """Value with a time stamp"""

    def __init__(self, value, timestamp) -> None:

        self.value = value
        """Data value."""

        self.timestamp = timestamp
        """Data value timestamp."""

