import sys
from ui.manager import UIManager
from services.worker import Worker
from PySide6 import QtWidgets
from services.login import isLoggedIn, createLocalAppPathIfNotExists, saveJWTLocally

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    createLocalAppPathIfNotExists()

    loggedIn = isLoggedIn()

    # init UIManager
    uimanager = UIManager()
    widget = uimanager.createUI(loggedIn)

    # start background worker when user is still logged in
    if loggedIn:
        worker = Worker()
        worker.start()

    sys.exit(app.exec())
