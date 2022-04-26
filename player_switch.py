#!/usr/bin/env python3

from PyQt5 import QtCore
from PyQt5.QtWidgets import *

import rclpy
from rclpy.node import Node

from rosbag2_interfaces.srv import (
    Pause,
    Resume,
    SetRate,
)

import functools
import sys

class SwitchWidget(QMainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUI()

    def setupUI(self):
        self.setObjectName("MainWindow")
        self.resize(480, 120)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setObjectName("gridLayout")

        self.rate_button = []
        for i, rate in enumerate([0.1, 0.5, 1.0]):
            btn = QPushButton(str(rate))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.rate_button.append(btn)
            self.gridLayout.addWidget(self.rate_button[-1], 0, i, 1, 1)

        self.button = QPushButton('pause')
        self.button.setCheckable(True)
        self.button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.gridLayout.addWidget(self.button, 1, 0, 1, -1)
        self.setCentralWidget(self.centralwidget)
    
    def onSetRate(self, button):

        print(button.text(), button)


class SwitchNode(Node):
    def __init__(self):
        super().__init__('SwitchNode')
        # Qt
        self.widget = SwitchWidget()
        self.widget.show()
        self.widget.button.clicked.connect(self.onPushed)
        
        for btn in self.widget.rate_button:
            btn.clicked.connect(functools.partial(self.onSetRate, btn))

        # ROS
        self.pause_client = self.create_client(Pause, '/rosbag2_player/pause')
        self.resume_client = self.create_client(Resume, '/rosbag2_player/resume')
        self.rate_client = self.create_client(SetRate, '/rosbag2_player/set_rate')
    
    def onPushed(self, event):
        if self.widget.button.isChecked():
            future = self.pause_client.call_async(Pause.Request())
            future.result()
        else:
            future = self.resume_client.call_async(Resume.Request())
            future.result()

    def onSetRate(self, button):
        future = self.rate_client.call_async(SetRate.Request(rate=float(button.text())))
        future.result()


def main(args=None):
    app = QApplication(sys.argv)

    rclpy.init(args=args)
    node = SwitchNode()

    while True:
        app.processEvents()
        rclpy.spin_once(node, timeout_sec=0.01)

if __name__ == '__main__':
    main()
