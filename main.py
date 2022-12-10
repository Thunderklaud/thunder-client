import sys
from threading import Thread
from ui.manager import UIManager
from services.thundersynchandler import ThunderSyncHandler
from PySide6 import QtWidgets
from services.login import isLoggedIn
from services.localappmanager import LocalAppManager
from services.login import doAfterLoginActions

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    if False:
        sync_handler = ThunderSyncHandler()
        sync_handler.run()
    else:
        # prepare local app path
        LocalAppManager.createLocalAppPathIfNotExists()

        # get login state
        loggedIn = isLoggedIn()

        # init UIManager
        uimanager = UIManager()
        uimanager.createUI(loggedIn)

        # start background worker when user is logged in on startup
        doAfterLoginActions()

    sys.exit(app.exec())
