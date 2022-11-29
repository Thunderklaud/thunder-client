from ui.loginui import LoginUI
from ui.settingsui import SettingsUI
from PySide6 import QtWidgets
from services.login import doAfterLoginActions


class UIManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.settingsWindow = None
        self.loginWindow = None

    def createUI(self, loggedIn):
        if loggedIn:
            self.openSettingsWindow()
        else:
            self.openLoginWindow()

    def openLoginWindow(self):
        # close other windows
        if self.settingsWindow is not None:
            self.settingsWindow.close()
            self.settingsWindow = None

        self.loginWindow = LoginUI(self.openSettingsWindow)
        self.loginWindow.resize(250, 250)
        self.loginWindow.show()
        self.loginWindow.setWindowTitle("Thunderklaud")

    def openSettingsWindow(self):
        # close other windows
        if self.loginWindow is not None:
            self.loginWindow.close()
            self.loginWindow = None

        self.settingsWindow = SettingsUI(self.openLoginWindow)
        self.settingsWindow.resize(350, 400)
        self.settingsWindow.setWindowTitle("Thunderklaud Settings")
        self.settingsWindow.show()
        
        doAfterLoginActions()
