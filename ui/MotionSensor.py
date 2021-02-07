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


event_display_time = datetime.timedelta(seconds=10)


class MotionSensorWidget(QWidget):
    def __init__(self, status, event_display_time = datetime.timedelta(seconds=10), *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.status = status
        self.hub_orientation_label = QLabel()
        self.hub_gesture_label = QLabel()

        ms_group = QGroupBox('Motion Sensor')
        layout = QFormLayout(ms_group)
        layout.addRow('Hub Orientation:', self.hub_orientation_label)
        layout.addRow('Hub Gesture:', self.hub_gesture_label)

        layout = QVBoxLayout()
        layout.addWidget(ms_group)
        self.setLayout(layout)

    def refresh(self):
        now = datetime.datetime.now()
        status = self.status

        gesture = ''
        if now - status.motion_sensor.gesture.timestamp < event_display_time:
            gesture = status.motion_sensor.gesture.value

        self.hub_orientation_label.setText(status.motion_sensor.orientation.value)
        self.hub_gesture_label.setText(gesture)

