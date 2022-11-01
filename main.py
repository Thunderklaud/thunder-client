import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.text = QtWidgets.QLabel("Log in to your Thunderklaud")
        font = self.text.font()
        font.setPointSize(30)
        self.text.setFont(font)

        self.text.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.serverURLInput = QtWidgets.QLineEdit()
        self.serverURLInput.setPlaceholderText("Server URL")

        self.usernameInput = QtWidgets.QLineEdit()
        self.usernameInput.setPlaceholderText("Username")

        self.passwordInput = QtWidgets.QLineEdit()
        self.passwordInput.setPlaceholderText("Password")

        self.loginButton = QtWidgets.QPushButton("Login")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.topLayout = QtWidgets.QVBoxLayout()
        self.setStyleSheet("background-color:#dddddd;")
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.serverURLInput)
        self.layout.addWidget(self.usernameInput)
        self.layout.addWidget(self.passwordInput)
        self.layout.addWidget(self.loginButton)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(400, 400)

    widget.show()

    sys.exit(app.exec())
