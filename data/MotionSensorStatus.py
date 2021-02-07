from data.TimeStampedData import TimeStampedData
import datetime
import logging


logger = logging.getLogger(__name__)


string_to_category_mapping = {
    'front': 1,
    'back': 1,
    'up': 1,
    'down': 1,
    'leftside': 1,
    'rightside': 1,

    'shake': 2,
    'tapped': 2,
    'doubletapped': 2,
    'freefall': 2,
}


class MotionSensorStatus(object):
    """Status of the hub motion sensor."""

    def __init__(self) -> None:
        super().__init__()

        self.orientation = TimeStampedData(None, datetime.datetime.now())
        """Last hub orientation recorded."""

        self.gesture = TimeStampedData(None, datetime.datetime.now())
        """Last gesture reorded."""

    def record_orientation(self, timestamp : datetime.datetime, orientation : str):
        self.orientation = TimeStampedData(orientation, timestamp)

    def record_gesture(self, timestamp : datetime.datetime, gesture : str):
        self.gesture = TimeStampedData(gesture, timestamp)

    def record_event(self, timestamp : datetime.datetime, value : str):
        category = string_to_category_mapping[value] if value in string_to_category_mapping else -1
        if category == 1:
            self.record_orientation(timestamp, value)
        elif category == 2:
            self.record_gesture(timestamp, value)
        else:
            logging.error('unrecognized motion sensor value: %s', value)
