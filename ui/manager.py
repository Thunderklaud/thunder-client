from ui.loginui import LoginUI
from ui.settingsui import SettingsUI
from PySide6 import QtWidgets


class UIManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def createUI(self, loggedIn):
        if loggedIn:
            widget = SettingsUI()
            widget.resize(350, 400)
            widget.show()
            widget.setWindowTitle("Thunderklaud Settings")
        else:
            widget = LoginUI()
            widget.resize(250, 250)
            widget.show()
            widget.setWindowTitle("Thunderklaud")

        return widget
