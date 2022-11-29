import sys
from threading import Thread
from ui.manager import UIManager
from services.worker import Worker
from services.foldersyncer import FolderSyncer
from PySide6 import QtWidgets
from services.login import isLoggedIn
from services.localappmanager import LocalAppManager

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    if False:
        folder_syncer = FolderSyncer()
        folder_syncer.run()
        sys.exit()

    # prepare local app path
    LocalAppManager.createLocalAppPathIfNotExists()

    # get login state
    loggedIn = isLoggedIn()

    # init UIManager
    uimanager = UIManager()
    uimanager.createUI(loggedIn)

    # start background worker when user is logged in on startup
    if loggedIn:
        worker = Worker()
        worker.start()

    sys.exit(app.exec())
