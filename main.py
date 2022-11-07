import sys
from ui.loginui import LoginUI
from services.worker import Worker
from PySide6 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = LoginUI()
    widget.resize(250, 250)
    widget.show()
    widget.setWindowTitle("Thunderklaud")

    worker = Worker()
    worker.start()

    sys.exit(app.exec())
