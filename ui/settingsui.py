import sys
from PySide6 import QtCore, QtWidgets, QtGui
from services.worker import Worker


class SettingsUI(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.createLayouts()
        self.createTopBar()
        self.createMainContent()
        self.createBottomBar()

    def createLayouts(self):
        self.topBarLayout = QtWidgets.QHBoxLayout()
        self.topBarLayout.setAlignment(QtCore.Qt.AlignTop)
        self.contentLayout = QtWidgets.QVBoxLayout()
        self.bottomBarLayout = QtWidgets.QHBoxLayout()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.topBarLayout)
        self.layout.addLayout(self.contentLayout)
        self.layout.addLayout(self.bottomBarLayout)

    def createTopBar(self):
        headline = QtWidgets.QLabel("Thunderklaud Settings")
        font = headline.font()
        font.setPointSize(12)
        headline.setFont(font)
        self.topBarLayout.addWidget(headline)

        self.createLogoutButton()

    def createMainContent(self):
        settingsBox = QtWidgets.QGroupBox("Settings")
        self.settingsBoxLayout = QtWidgets.QVBoxLayout()
        self.createLocalSyncPathInput()
        settingsBox.setLayout(self.settingsBoxLayout)
        self.contentLayout.addWidget(settingsBox)

        aboutBox = QtWidgets.QGroupBox("About")
        self.aboutBoxLayout = QtWidgets.QVBoxLayout()
        aboutLine1 = QtWidgets.QLabel("Thunderklaud Desktop-Client")
        self.aboutBoxLayout.addWidget(aboutLine1)
        aboutLine2 = QtWidgets.QLabel("Version 1.0.0")
        self.aboutBoxLayout.addWidget(aboutLine2)

        aboutLine3 = QtWidgets.QLabel(
            "More information: <a href='https://github.com/Thunderklaud/thunder-client' target='_blank'>GitHub</a>")
        aboutLine3.setOpenExternalLinks(True)
        self.aboutBoxLayout.addWidget(aboutLine3)

        aboutBox.setLayout(self.aboutBoxLayout)
        self.contentLayout.addWidget(aboutBox)

    def createBottomBar(self):
        self.createSaveButton()

    def createLocalSyncPathInput(self):
        rowLayout = QtWidgets.QHBoxLayout()

        syncFolderPathLabel = QtWidgets.QLabel("Local Sync Folder")
        rowLayout.addWidget(syncFolderPathLabel)

        syncFolderPath = Worker.getSyncFolderPath()
        localSynyPathInput = QtWidgets.QLineEdit(syncFolderPath)
        rowLayout.addWidget(localSynyPathInput)

        self.settingsBoxLayout.addLayout(rowLayout)

    def createSaveButton(self):
        saveButton = QtWidgets.QPushButton("Save")
        self.bottomBarLayout.addWidget(saveButton)

    def createLogoutButton(self):
        logoutButton = QtWidgets.QPushButton("Logout")
        self.topBarLayout.addWidget(logoutButton)
