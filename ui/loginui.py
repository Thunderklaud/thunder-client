import sys
from PySide6 import QtCore, QtWidgets, QtGui
import requests
from services.login import login, register


class LoginUI(QtWidgets.QWidget):
    def __init__(self, openSettingsScreen):
        super().__init__()

        self.openSettingsScreen = openSettingsScreen

        self.text = QtWidgets.QLabel("Log in to your Thunderklaud")
        font = self.text.font()
        font.setPointSize(12)
        self.text.setFont(font)

        self.text.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.loginFeedback = QtWidgets.QLabel("")

        self.serverURLInput = QtWidgets.QLineEdit("https://thunderklaud-api.web2ju.de/")
        self.serverURLInput.setPlaceholderText("Server URL")

        self.usernameInput = QtWidgets.QLineEdit("@")  # TestData
        self.usernameInput.setPlaceholderText("Username")

        self.passwordInput = QtWidgets.QLineEdit("0")  # TestData
        self.passwordInput.setPlaceholderText("Password")

        self.loginButton = QtWidgets.QPushButton("Login")
        self.loginButton.clicked.connect(self.clickedLogin)
        # self.loginButton.setStyleSheet('background-color:red;')

        self.registerButton = QtWidgets.QPushButton("Register")
        self.registerButton.clicked.connect(self.clickedRegister)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.topLayout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.loginFeedback)
        self.layout.addWidget(self.serverURLInput)
        self.layout.addWidget(self.usernameInput)
        self.layout.addWidget(self.passwordInput)
        self.layout.addWidget(self.loginButton)
        self.layout.addWidget(self.registerButton)

    def clickedRegister(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()
        #"M" and "W" just DummyData
        register("M", "w", username, password)

    def clickedLogin(self):
        mail = self.usernameInput.text()
        pw = self.passwordInput.text()
        serverURL = self.serverURLInput.text()
        loginFeedbackText = login(mail, pw, serverURL, self.openSettingsScreen)
        self.loginFeedback.setText(loginFeedbackText)
