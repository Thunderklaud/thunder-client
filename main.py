import sys
from ui.manager import UIManager
from services.worker import Worker
from PySide6 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    # TODO: Check if local JWT is valid
    loggedIn = False

    # init UIManager
    uimanager = UIManager()
    widget = uimanager.createUI(loggedIn)

    # start background worker when user is still logged in
    if loggedIn:
        worker = Worker()
        worker.start()

    sys.exit(app.exec())
