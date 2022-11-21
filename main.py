import sys
from ui.manager import UIManager
from services.worker import Worker
from PySide6 import QtWidgets
from services.login import isLoggedIn
from services.localappmanager import LocalAppManager

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    # prepare local app path
    # localAppManager = LocalAppManager()
    LocalAppManager.createLocalAppPathIfNotExists()

    # get login state
    loggedIn = isLoggedIn()

    # init UIManager
    uimanager = UIManager()
    widget = uimanager.createUI(loggedIn)

    # start background worker when user is logged in on startup
    if loggedIn:
        worker = Worker()
        worker.start()

    sys.exit(app.exec())
