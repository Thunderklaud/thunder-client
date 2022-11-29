from ui.loginui import LoginUI
from ui.settingsui import SettingsUI
from PySide6 import QtWidgets
from services.login import doAfterLoginActions


class UIManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def createUI(self, loggedIn):
        self.widget = QtWidgets.QStackedWidget()

        self.widget.addWidget(SettingsUI(self.openLoginScreen))
        self.widget.addWidget(LoginUI(self.openSettingsScreen))

        if loggedIn:
            self.openSettingsScreen()
        else:
            self.openLoginScreen()

        return self.widget

    def openLoginScreen(self):
        self.widget.setCurrentIndex(1)
        self.widget.resize(250, 250)
        self.widget.show()
        self.widget.setWindowTitle("Thunderklaud")

    def openSettingsScreen(self):
        self.widget.setCurrentIndex(0)
        self.widget.resize(350, 400)
        self.widget.show()
        self.widget.setWindowTitle("Thunderklaud Settings")

        doAfterLoginActions()
