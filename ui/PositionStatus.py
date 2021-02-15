#! /usr/bin/python3

import datetime
import logging
import os
import sys

from comm.HubClient import HubClient
from data.HubMonitor import HubMonitor
from data.HubStatus import HubStatus
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget


event_display_time = datetime.timedelta(seconds=10)


class PositionStatusWidget(QWidget):
    def __init__(self, status, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.status = status
        self.orientation_label = QLabel()
        self.gyro_label = QLabel()
        self.accel_label = QLabel()

        pos_group = QGroupBox('Position')
        layout = QFormLayout(pos_group)
        layout.addRow('Tilt Angle:', self.orientation_label)
        layout.addRow('Gyro Rate:', self.gyro_label)
        layout.addRow('Accelerometer:', self.accel_label)

        layout = QVBoxLayout()
        layout.addWidget(pos_group)
        self.setLayout(layout)

    def refresh(self):
        status = self.status

        self.orientation_label.setText('Yaw: {} Pitch: {} Roll: {}'.format(*status.orientation()))
        self.gyro_label.setText('X: {}  Y: {}  Z: {}'.format(*status.gyroscope()))
        self.accel_label.setText('X: {}  Y: {}  Z: {}'.format(*status.accelerometer()))


