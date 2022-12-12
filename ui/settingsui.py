import sys
import json
from PySide6 import QtCore, QtWidgets, QtGui
from services.worker import Worker
from services.serversettings import ServerSettings
from services.localappmanager import LocalAppManager
from services.login import logout


class SettingsUI(QtWidgets.QWidget):

    def __init__(self, openLoginScreen):
        super().__init__()

        self.openLoginScreen = openLoginScreen
        self.createLayouts()
        self.createTopBar()
        self.createMainContent()
        self.createBottomBar()

    def createLayouts(self):
        self.topBarLayout = QtWidgets.QHBoxLayout()
        self.topBarLayout.setAlignment(QtCore.Qt.AlignTop)
        self.contentLayout = QtWidgets.QVBoxLayout()
        self.bottomBarLayout = QtWidgets.QVBoxLayout()

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
        self.createSyncDirectoriesArea()
        self.createSettingsArea()
        self.createAboutArea()

    def createSyncDirectoriesArea(self):
        syncDirectoriesBox = QtWidgets.QGroupBox("Sync Directories")
        self.syncDirectoriesLayout = QtWidgets.QVBoxLayout()

        self.refresh_button = QtWidgets.QPushButton("↻")
        self.refresh_button.setToolTip(
            "Fetch the newest directories from the server")
        self.refresh_button.clicked.connect(self.addSyncDirectories)
        self.syncDirectoriesLayout.addWidget(self.refresh_button)

        syncDirectories = ServerSettings.getSyncDirectories()
        self.addSyncDirectoryRecursive(syncDirectories)

        syncDirectoriesBox.setLayout(self.syncDirectoriesLayout)
        self.contentLayout.addWidget(syncDirectoriesBox)

    def addSyncDirectories(self):
        self.refresh_button.setText("Loading...")

        # remove all directories checkboxes
        count = self.syncDirectoriesLayout.count()
        for i in range(1, count):
            item = self.syncDirectoriesLayout.itemAt(1).widget()
            item.setParent(None)

        syncDirectories = ServerSettings.getSyncDirectories()
        self.addSyncDirectoryRecursive(syncDirectories)

        self.refresh_button.setText("↻")

    def addSyncDirectoryRecursive(self, directory, level=0):
        perLevelPadding = 7

        for dir in directory:
            checkbox = QtWidgets.QCheckBox(dir["name"], self)
            checkbox.setStyleSheet(
                "margin-left: " + str(level * perLevelPadding) + "px")
            self.syncDirectoriesLayout.addWidget(checkbox)

            if "children" in dir and len(dir["children"]):
                self.addSyncDirectoryRecursive(dir["children"], level + 1)

    def createSettingsArea(self):
        settingsBox = QtWidgets.QGroupBox("Settings")
        self.settingsBoxLayout = QtWidgets.QVBoxLayout()
        self.createLocalSyncPathInput()
        settingsBox.setLayout(self.settingsBoxLayout)
        self.contentLayout.addWidget(settingsBox)

    def createAboutArea(self):
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

        syncDirectoryPathLabel = QtWidgets.QLabel("Local Sync Directory")
        rowLayout.addWidget(syncDirectoryPathLabel)

        syncDirectoryPath = LocalAppManager.getSetting(
            "local_sync_folder_path")
        localSynyPathInput = QtWidgets.QLineEdit(syncDirectoryPath)
        rowLayout.addWidget(localSynyPathInput)

        self.settingsBoxLayout.addLayout(rowLayout)

    def createSaveButton(self):
        saveButton = QtWidgets.QPushButton("Save")
        saveButton.clicked.connect(self.clickedSave)
        self.bottomBarLayout.addWidget(saveButton)

    def clickedSave(self):
        print(">>>Save<<<")
        aList = [{"a": 54, "b": 87}, {"c": 81, "d": 63}, {"e": 17, "f": 39}]
        jsonString = json.dumps(aList)
        path = LocalAppManager.getLocalAppPath() + "settings.json"
        print("Path::: " + path)

        jsonFile = open(path, "w")
        jsonFile.write(jsonString)
        jsonFile.close()

    def createLogoutButton(self):
        logoutButton = QtWidgets.QPushButton("Logout")
        logoutButton.clicked.connect(self.clickedLogout)
        self.topBarLayout.addWidget(logoutButton)

    def clickedLogout(self):
        if logout(self.openLoginScreen):
            self.showNotification("Successfully logged out!")
        else:
            self.showNotification("Error: Logout not possible!")

    def showNotification(self, text):
        # remove old notifcation if exists
        oldNotification = self.bottomBarLayout.itemAt(1)
        if oldNotification is not None:
            oldNotification.widget().setParent(None)

        # add new notification
        notification = QtWidgets.QLabel(text)
        self.bottomBarLayout.addWidget(notification)
