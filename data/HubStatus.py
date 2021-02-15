from data.MotionSensorStatus import MotionSensorStatus


device_id_to_name_mapping = {
    0: '', # no device connected
    61: 'Color Sensor', 
    62: 'Distance Sensor', 
    75: 'Motor'
    }

def device_name(id):
    """Map the device id to name.  Empty string returned for no device connected."""
    return device_id_to_name_mapping[id] if id in device_id_to_name_mapping else 'Unknown Device'


class HubStatus(object):
    def __init__(self):
        self.status0 = [[0,[]]] * 6 + [['','','']] * 3 + ['', 0]
        """Values obtained from the m=0 message.
        
        Array of 11 values:
        * Entries 0-5 are each an array of length 2, corresponding to ports A-F
          - first entry is device ID
          - second entry is device status (varies by device)
        * Entry 6 is accelerometer; array of 3 acceleration values (x,y,z)
        * Entry 7 is gyroscope; array of 3 rate values (x,y,z)
        * Entry 8 is orientation; array of 3 values (yaw,pitch,roll)
        * Entry 9 is a string
        * Entry 10 is an int        
        """

        self.status2 = [0.0, 0, False]
        """Values obtained from the m=2 message.
        
        Array of 3 values:
        * Entry 0 is a float (typically 8.3 ish)
        * Entry 1 is int (battery %)
        * Entry 2 is bool (USB connected)
        """

        self.motion_sensor = MotionSensorStatus()

    def set_status0(self, status):
        self.status0 = status

    def set_status2(self, status):
        self.status2 = status

    def port_raw(self, port):
        if port > 5: raise IndexError('port index range 0-5')
        return self.status0[port]

    def port_device_id(self, port):
        return self.port_raw(port)[0]

    def port_device_name(self, port):
        return device_name(self.port_device_id(port))

    def port_device_data(self, port):
        return self.port_raw(port)[1]

    def accelerometer(self):
        """Acceleration (ax,ay,az)"""
        return self.status0[6]

    def gyroscope(self):
        """Gyroscope rate (rx,ry,rz)"""
        return self.status0[7]

    def orientation(self):
        """Orientation angles (yaw, pitch, roll)"""
        return self.status0[8]

    @property
    def is_usb_connected(self):
        return self.status2[2]

    @property
    def battery_level(self):
        """Battery charge percentage."""
        return self.status2[1]
 