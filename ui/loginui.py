import sys
from PySide6 import QtCore, QtWidgets, QtGui
from ui.settingsui import SettingsUI


class LoginUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.text = QtWidgets.QLabel("Log in to your Thunderklaud")
        font = self.text.font()
        font.setPointSize(12)
        self.text.setFont(font)

        self.text.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.loginFeedback = QtWidgets.QLabel("")

        self.serverURLInput = QtWidgets.QLineEdit()
        self.serverURLInput.setPlaceholderText("Server URL")

        self.usernameInput = QtWidgets.QLineEdit()
        self.usernameInput.setPlaceholderText("Username")

        self.passwordInput = QtWidgets.QLineEdit()
        self.passwordInput.setPlaceholderText("Password")

        self.loginButton = QtWidgets.QPushButton("Login")
        self.loginButton.clicked.connect(self.login)
        # self.loginButton.setStyleSheet('background-color:red;')

        self.layout = QtWidgets.QVBoxLayout(self)
        self.topLayout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.loginFeedback)
        self.layout.addWidget(self.serverURLInput)
        self.layout.addWidget(self.usernameInput)
        self.layout.addWidget(self.passwordInput)
        self.layout.addWidget(self.loginButton)

    def login(self):
        # TODO: do server authentication here
        self.loginFeedback.setText("You're now logged in...")

        # TODO: save JWT to local machine

        # TODO: Open Settings page
