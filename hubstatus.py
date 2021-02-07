#! /usr/bin/python3

import datetime
import logging
import os
import sys
from ui.DevicePortWidget import DevicePortWidget
from ui.ConnectionWidget import ConnectionWidget

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget

from comm.HubClient import HubClient
from data.HubMonitor import HubMonitor
from data.HubStatus import HubStatus
from ui.DeviceStatusWidget import DeviceStatusWidget
from utils.setup import setup_logging

logger = logging.getLogger("App")

log_filename = os.path.dirname(__file__) + "/logs/hubstatus.log"
setup_logging(log_filename)



class MainWindow(QMainWindow):
    def __init__(self, hub_client, hub_monitor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hub_monitor = hub_monitor

        mw = QWidget(self)
        layout = QVBoxLayout()

        layout.addWidget(ConnectionWidget(hub_client))

        self.onboard_dev = DeviceStatusWidget(hub_monitor.status)
        layout.addWidget(self.onboard_dev)

        self.device_ports = DevicePortWidget(hub_monitor.status)
        layout.addWidget(self.device_ports)

        mw.setLayout(layout)
        self.setCentralWidget(mw)
        self.setMinimumSize(400,800)

        # Timer refresh trick from https://github.com/Taar2/pyqt5-modelview-tutorial/blob/master/modelview_3.py
        # this trick is used to work around the issue of updating UI from background threads -- i.e. events
        # raised by HubClient.
        timer = QtCore.QTimer(self)
        timer.setInterval(200)
        timer.timeout.connect(self.refresh)
        timer.start()

    def refresh(self):
        self.onboard_dev.refresh()
        self.device_ports.refresh()


logger.info("LEGO status app starting up")
hc = HubClient()
monitor = HubMonitor(hc)

app = QApplication(sys.argv)
window = MainWindow(hc, monitor)
window.setWindowTitle('LEGO Hub Status')
window.show()

hc.start()
sys.exit(app.exec_())
