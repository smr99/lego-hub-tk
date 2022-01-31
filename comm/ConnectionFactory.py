# Factory method to construct a suitable ConnectionMonitor based on configuration.

import logging
from comm.DirectConnectionMonitor import DirectConnectionMonitor

logger = logging.getLogger(__name__)


def make_connection_monitor(config):
    if 'connection' in config:
        connection_type = config['connection']
    else:
        logger.warn('no connection configured; will use serial connection')
        connection_type = 'serial'

    if connection_type == 'serial':
        return make_connection_monitor_serial(config)
    elif connection_type == 'bluetooth':
        return make_connection_monitor_bluetooth(config)
    elif connection_type == 'multiplexed':
        return make_connection_monitor_multiplexed(config)
    else:
        raise ValueError("configuration parameter connection has invalid value: " + connection_type)

def make_connection_monitor_serial(config):
    if 'serial' in config:
        device_name = config['serial']['device']
    else:
        device_name = 'auto'

    logger.info('connecting to hub using serial device: %s', device_name)    
    
    if device_name == 'auto':
        from comm.UsbConnectionMonitor import UsbConnectionMonitor
        return UsbConnectionMonitor()
    else:
        from comm.SerialConnection import SerialConnection
        return DirectConnectionMonitor(SerialConnection(device_name))

def make_connection_monitor_bluetooth(config):
    bt_params = config['bluetooth']
    from comm.BluetoothConnection import BluetoothConnection
    return DirectConnectionMonitor(BluetoothConnection(bt_params['address'], bt_params['port']))

def make_connection_monitor_multiplexed(config):
    bt_params = config['bluetooth']
    from comm.MultiplexedConnectionMonitor import MultiplexedConnectionMonitor
    return MultiplexedConnectionMonitor(bt_params['address'], bt_params['port'])
