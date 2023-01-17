import sys
import json
from PySide6 import QtCore, QtWidgets
from services.server_settings import ServerSettings
from ui.settings_interval_handler import SettingsIntervalHandler
from services.localappmanager import LocalAppManager
from services.login import logout
from services.thundersynchandler import ThunderSyncHandler
from services.permanent_sync_handler import PermanentSyncHandler


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

    def createMainContent(self):

        self.createInfoArea()
        self.createActionsArea()
        self.createSyncDirectoriesArea()
        self.createSettingsArea()
        self.createAboutArea()

    def createInfoArea(self):
        infoBox = QtWidgets.QGroupBox("Info")
        self.infoBoxLayout = QtWidgets.QVBoxLayout()
        infoBox.setLayout(self.infoBoxLayout)

        # add ServerURL
        urlString = "Server URL: " + LocalAppManager.getSetting("serverURL")
        serverURLLabel = QtWidgets.QLabel(urlString)
        font = serverURLLabel.font()
        font.setPointSize(8)
        serverURLLabel.setFont(font)
        self.infoBoxLayout.addWidget(serverURLLabel)

        # add Status Badge with async Handler
        statusBadge = QtWidgets.QLabel("Status: unknown")
        settingsIntervalHandler = SettingsIntervalHandler()
        settingsIntervalHandler.run(statusBadge)
        self.infoBoxLayout.addWidget(statusBadge)

        self.contentLayout.addWidget(infoBox)

    def createActionsArea(self):
        actionsBox = QtWidgets.QGroupBox("Actions")
        self.actionsBoxLayout = QtWidgets.QVBoxLayout()
        actionsBox.setLayout(self.actionsBoxLayout)

        # create LogoutButton
        logoutButton = QtWidgets.QPushButton("Logout")
        logoutButton.clicked.connect(self.clickedLogout)
        self.actionsBoxLayout.addWidget(logoutButton)

        # create ReSyncButton
        reSyncButton = QtWidgets.QPushButton("ReSync")
        reSyncButton.clicked.connect(self.clickedReSync)
        self.actionsBoxLayout.addWidget(reSyncButton)

        self.contentLayout.addWidget(actionsBox)

    def createSyncDirectoriesArea(self):
        syncDirectoriesBox = QtWidgets.QGroupBox("Sync Directories")
        self.syncDirectoriesLayout = QtWidgets.QVBoxLayout()

        infoText = QtWidgets.QLabel(
            "All <u>checked</u> folders will be synced with the Cloud.")
        self.syncDirectoriesLayout.addWidget(infoText)

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
            checkboxLabel = dir["name"]

            checkbox = QtWidgets.QCheckBox(checkboxLabel, self)
            checkbox.setObjectName(dir["id"])
            checkbox.setChecked(dir["syncDir"])
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
        aboutLine2 = QtWidgets.QLabel("Version 1.1.3")
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

        syncFolderPath = LocalAppManager.getSetting("syncFolderPath")
        self.localSyncPathInput = QtWidgets.QLineEdit(syncFolderPath)
        rowLayout.addWidget(self.localSyncPathInput)

        self.settingsBoxLayout.addLayout(rowLayout)

    def getLocalSyncPathInput(self):
        return self.localSyncPathInput.text()

    def createSaveButton(self):
        saveButton = QtWidgets.QPushButton("Save")
        saveButton.setToolTip(
            "Save all settings")
        saveButton.clicked.connect(self.clickedSave)
        self.bottomBarLayout.addWidget(saveButton)

    def clickedSave(self):
        settings = LocalAppManager.loadSettings()

        settings["syncFolderPath"] = self.getLocalSyncPathInput()
        settings["notToSyncFolders"] = self.getFoldersNotToSync()

        LocalAppManager.saveSettings(settings)

        # show saved dialog
        self.showSavedDialog()

    def showSavedDialog(self):
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle("Information")
        dialog.setText("Settings successfully saved")
        dialog.exec()

    def clickedLogout(self):
        if logout(self.openLoginScreen):
            self.showNotification("Successfully logged out!")
        else:
            self.showNotification("Error: Logout not possible!")

    def clickedReSync(self):
        permanentSyncHandler = PermanentSyncHandler()
        permanentSyncHandler.runStartup()

    def showNotification(self, text):
        # remove old notifcation if exists
        oldNotification = self.bottomBarLayout.itemAt(1)
        if oldNotification is not None:
            oldNotification.widget().setParent(None)

        # add new notification
        notification = QtWidgets.QLabel(text)
        self.bottomBarLayout.addWidget(notification)

    def getFoldersNotToSync(self):
        count = self.syncDirectoriesLayout.count()
        objectNames = []
        for i in range(1, count):
            item = self.syncDirectoriesLayout.itemAt(i).widget()
            if not item.isChecked():
                objectNames.append(item.objectName())
        return objectNames

    def closeEvent(self, event):
        ThunderSyncHandler.STATUS = 0
        PermanentSyncHandler.RUNNING = False
        SettingsIntervalHandler.RUNNING = False
