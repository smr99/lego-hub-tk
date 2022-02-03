#! /usr/bin/python3

import base64
from data.ProgramHubLogger import ProgramHubLogger
from datetime import datetime
import logging
import os
import sys
from ui.MotionSensor import MotionSensorWidget
from ui.PositionStatus import PositionStatusWidget
from ui.DevicePortWidget import DevicePortWidget
from ui.ConnectionWidget import ConnectionWidget

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget

from comm.HubClient import ConnectionState, HubClient
from data.HubMonitor import HubMonitor
from data.HubStatus import HubStatus
from ui.DeviceStatusWidget import DeviceStatusWidget
from utils.setup import setup_logging

logger = logging.getLogger("App")

log_filename = os.path.dirname(__file__) + "/logs/hubcontrol.log"
setup_logging(log_filename)


def list_programs(info):
    storage = info['storage']
    slots = info['slots']
    print("%4s %-40s %6s %-20s %-12s %-10s" % ("Slot", "Decoded Name", "Size",  "Last Modified", "Project_id", "Type"))
    for i in range(20):
        if str(i) in slots:
            sl = slots[str(i)]
            modified = datetime.utcfromtimestamp(sl['modified']/1000).strftime('%Y-%m-%d %H:%M:%S')
            try:
                decoded_name = base64.b64decode(sl['name']).decode('utf-8')
            except:
                decoded_name = sl['name']
            try:
                project = sl['project_id']
            except:
                project = " "
            try:
                type = sl['type']
            except:
                type = " "
            print("%4s %-40s %5db %-20s %-12s %-10s" % (i, decoded_name, sl['size'], modified, project, type))
    print(("Storage free %s%s of total %s%s" % (storage['free'], storage['unit'], storage['total'], storage['unit'])))
    

class ConsoleWidget(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)


    def append(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())

    def append_line(self, text): self.append(text + '\n')

class ProgramWidget(QWidget):
    def __init__(self, hub_client : HubClient, hub_monitor : HubMonitor, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._client = hub_client
        self._monitor = hub_monitor
        self._executing_program_label = QLabel()
        self._slot_spinbox = QSpinBox()
        self._run_button = QPushButton('Run')
        self._run_button.clicked.connect(self.run_program)
        self._stop_button = QPushButton('Stop')
        self._stop_button.clicked.connect(self.stop_program)

        runstop_widget = QWidget()
        layout = QHBoxLayout(runstop_widget)
        layout.addWidget(QLabel('Slot:'))
        layout.addWidget(self._slot_spinbox)
        layout.addWidget(self._run_button)
        layout.addWidget(self._stop_button)

        box = QGroupBox('Program Execution')
        layout = QFormLayout(box)
        layout.addRow('Executing Program ID:', self._executing_program_label)
        layout.addRow(runstop_widget)

        layout = QVBoxLayout()
        layout.addWidget(box)
        self.setLayout(layout)

    def refresh(self):
        is_connected = self._client.state == ConnectionState.TELEMETRY
        self._executing_program_label.setText(self._monitor.execution_status[0])
        self._run_button.setEnabled(is_connected)
        self._stop_button.setEnabled(is_connected)

    def run_program(self):
        slot = self._slot_spinbox.value()
        r = self._client.program_execute(slot)
        logger.debug('Program execute returns: %s', r)

    def stop_program(self):
        r = self._client.program_terminate()
        logger.debug('Program terminate returns: %s', r)


class MainWindow(QMainWindow):
    def __init__(self, hub_client, hub_monitor, *args, **kwargs):
        super().__init__(*args, **kwargs)

        status = hub_monitor.status

        self._client = hub_client
        self._hub_monitor = hub_monitor

        self.position_widget = PositionStatusWidget(status)
        self.motion_widget = MotionSensorWidget(status)
        self.program_widget = ProgramWidget(hub_client, hub_monitor)

        self.port_widget = DevicePortWidget(status)
        self.console = ConsoleWidget()

        self.list_button = QPushButton('List')
        self.list_button.clicked.connect(self.list_programs)

        # Top row (status)
        top_box = QWidget()
        layout = QHBoxLayout(top_box)
        layout.addWidget(ConnectionWidget(hub_client))
        layout.addWidget(self.position_widget)
        layout.addWidget(self.motion_widget)

        # Button bar
        buttons = QWidget()
        layout = QHBoxLayout(buttons)
        layout.addWidget(self.list_button)

        mw = QWidget()
        layout = QVBoxLayout(mw)
        layout.addWidget(top_box)
        layout.addWidget(buttons)
        layout.addWidget(self.program_widget)
        layout.addWidget(self.port_widget)
        layout.addWidget(self.console)
        self.setCentralWidget(mw)

        hub_monitor.events.console_print += self.console.append

        # Timer refresh trick from https://github.com/Taar2/pyqt5-modelview-tutorial/blob/master/modelview_3.py
        # this trick is used to work around the issue of updating UI from background threads -- i.e. events
        # raised by HubClient.
        timer = QtCore.QTimer(self)
        timer.setInterval(200)
        timer.timeout.connect(self.refresh)
        timer.start()

    def refresh(self):
        is_connected = self._client.state == ConnectionState.TELEMETRY
        is_connected_usb = is_connected and self._hub_monitor.status.is_usb_connected
        self.position_widget.refresh()
        self.motion_widget.refresh()
        self.port_widget.refresh()
        self.program_widget.refresh()

    def list_programs(self):
        storage_status = self._client.get_storage_status()
        if storage_status is not None:
            list_programs(storage_status)

    def run_program(self):
        slot = 4
        r = self._client.program_execute(slot)
        print('Program execute returns: ', r)

logger.info("LEGO status app starting up")
hc = HubClient()
monitor = HubMonitor(hc)
monitor.logger = ProgramHubLogger('logs/program')

app = QApplication(sys.argv)
window = MainWindow(hc, monitor)
window.setWindowTitle('LEGO Hub Status')
window.show()

hc.start()
sys.exit(app.exec_())
