import sys
from PySide6 import QtCore, QtWidgets, QtGui


class SettingsUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.text = QtWidgets.QLabel("Settings")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
