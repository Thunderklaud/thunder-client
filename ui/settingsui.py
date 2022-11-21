import sys
from PySide6 import QtCore, QtWidgets, QtGui
from services.worker import Worker
from services.serversettings import ServerSettings
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
        self.createSyncFoldersArea()
        self.createSettingsArea()
        self.createAboutArea()

    def createSyncFoldersArea(self):
        syncFoldersBox = QtWidgets.QGroupBox("Sync Folders")
        self.syncFoldersLayout = QtWidgets.QVBoxLayout()

        # syncFolders = ServerSettings.getSyncFolders()
        syncFolders = [
            {
                "id": {
                    "$oid": "636e7c5ff0feb145084ab214"
                },
                "name": "Documents",
                "children": [
                    {
                        "id": {
                            "$oid": "636e7c5ff0feb145084ab214"
                        },
                        "name": "Sub Docs 1",
                        "children": [
                            {
                                "id": {
                                    "$oid": "636e7c5ff0feb145084ab214"
                                },
                                "name": "Sub Sub Docs 1",
                            },
                        ]
                    },
                    {
                        "id": {
                            "$oid": "636e7c5ff0feb145084ab214"
                        },
                        "name": "Sub Docs 2",
                    }
                ]
            }
        ]
        self.addSyncFolderRecursive(syncFolders)

        syncFoldersBox.setLayout(self.syncFoldersLayout)
        self.contentLayout.addWidget(syncFoldersBox)

    def addSyncFolderRecursive(self, folder, level=0):
        perLevelPadding = 7

        for dir in folder:
            checkbox = QtWidgets.QCheckBox(dir["name"], self)
            checkbox.setStyleSheet(
                "margin-left: " + str(level * perLevelPadding) + "px")
            self.syncFoldersLayout.addWidget(checkbox)

            if "children" in dir and len(dir["children"]):
                self.addSyncFolderRecursive(dir["children"], level + 1)

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
