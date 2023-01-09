import sys
from threading import Thread
from ui.manager import UIManager
from PySide6 import QtWidgets
from services.login import isLoggedIn
from services.localappmanager import LocalAppManager
from services.login import doAfterLoginActions

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    # create internal structure
    LocalAppManager.doStartupActions()

    # get login state
    loggedIn = isLoggedIn()

    # init UI
    uimanager = UIManager()
    uimanager.createUI(loggedIn)
    uimanager.setIcon(app)

    # start background worker when user is logged in on startup
    doAfterLoginActions()

    sys.exit(app.exec())
