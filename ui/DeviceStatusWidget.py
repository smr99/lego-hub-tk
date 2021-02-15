#! /usr/bin/python3

from data.HubMonitor import HubMonitor
import datetime
import logging
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from comm.HubClient import HubClient
from data.HubStatus import HubStatus


logger = logging.getLogger("App")
event_display_time = datetime.timedelta(seconds=10)


class DeviceStatusWidget(QWidget):
    def __init__(self, status, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.status = status
        self.orientation_label = QLabel()
        self.gyro_label = QLabel()
        self.accel_label = QLabel()
        self.status0_9 = QLabel()
        self.status0_10 = QLabel()
        self.status2_0 = QLabel()
        self.battery_level = QLabel()
        self.usb_label = QLabel()
        self.hub_orientation_label = QLabel()
        self.hub_gesture_label = QLabel()

        pos_group = QGroupBox('Position')
        layout = QGridLayout()
        layout.addWidget(QLabel('Tilt Angle'), 0, 0)
        layout.addWidget(self.orientation_label, 0, 1)
        layout.addWidget(QLabel('Gyro Rate'), 1, 0)
        layout.addWidget(self.gyro_label, 1, 1)
        layout.addWidget(QLabel('Accelerometer'), 2, 0)
        layout.addWidget(self.accel_label, 2, 1)
        pos_group.setLayout(layout)        

        group2 = QGroupBox('Unknown')
        layout = QGridLayout()
        layout.addWidget(QLabel('Status0[9]'), 0, 0)
        layout.addWidget(self.status0_9, 0, 1)
        layout.addWidget(QLabel('Status0[10]'), 1, 0)
        layout.addWidget(self.status0_10, 1, 1)
        layout.addWidget(QLabel('Status2[0]'), 2, 0)
        layout.addWidget(self.status2_0, 2, 1)
        layout.addWidget(QLabel('Battery%'), 3, 0)
        layout.addWidget(self.battery_level, 3, 1)
        layout.addWidget(QLabel('USB Connected'), 4, 0)
        layout.addWidget(self.usb_label, 4, 1)
        group2.setLayout(layout)

        ms_group = QGroupBox('Motion Sensor')
        layout = QFormLayout(ms_group)
        layout.addRow('Hub Orientation:', self.hub_orientation_label)
        layout.addRow('Hub Gesture:', self.hub_gesture_label)


        layout = QVBoxLayout()
        layout.addWidget(pos_group)
        layout.addWidget(group2)
        layout.addWidget(ms_group)
        self.setLayout(layout)

    def refresh(self):
        now = datetime.datetime.now()
        status = self.status

        self.orientation_label.setText('Yaw: {} Pitch: {} Roll: {}'.format(*status.orientation()))
        self.gyro_label.setText('X: {}  Y: {}  Z: {}'.format(*status.gyroscope()))
        self.accel_label.setText('X: {}  Y: {}  Z: {}'.format(*status.accelerometer()))
        self.status0_9.setText(str(status.status0[9]))
        self.status0_10.setText(str(status.status0[10]))
        self.status2_0.setText(str(status.status2[0]))
        self.battery_level.setText(str(status.battery_level))
        self.usb_label.setText(str(status.is_usb_connected))

        gesture = ''
        if now - status.motion_sensor.gesture.timestamp < event_display_time:
            gesture = status.motion_sensor.gesture.value

        self.hub_orientation_label.setText(status.motion_sensor.orientation.value)
        self.hub_gesture_label.setText(gesture)

