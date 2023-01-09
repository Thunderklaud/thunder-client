from pathlib import Path
import os
import json


class LocalAppManager():

    @staticmethod
    def getLocalAppPath():
        home = str(Path.home())
        appDir = "/.thunderklaud/"
        return home + appDir

    @staticmethod
    def getLocalJWTPath():
        return LocalAppManager.getLocalAppPath() + "jwt"

    @staticmethod
    def createLocalAppPathIfNotExists():
        localAppPath = LocalAppManager.getLocalAppPath()
        if not os.path.isdir(localAppPath):
            os.makedirs(localAppPath)

    @staticmethod
    def saveJWTLocally(jwt):
        localJWTPath = LocalAppManager.getLocalJWTPath()

        with open(localJWTPath, 'w') as f:
            f.write(jwt)

    @staticmethod
    def readLocalJWT():
        localJWTPath = LocalAppManager.getLocalJWTPath()
        if not os.path.exists(localJWTPath):
            return ""

        jwtFile = open(localJWTPath, "r")
        return jwtFile.read()

    @staticmethod
    def createDefaultSettingsJson():

        # if settings.json already exists
        path = LocalAppManager.getLocalAppPath() + "settings.json"
        if os.path.exists(path):
            return

        defaultServerURL = "http://localhost:8080/"
        defaultSyncFolderPath = "./test/client/"

        settings = {}

        settings["serverUrl"] = defaultServerURL
        settings["syncFolderPath"] = defaultSyncFolderPath
        settings["notToSyncFolders"] = []

        settings = json.dumps(settings)

        jsonFile = open(path, "w")
        jsonFile.write(settings)
        jsonFile.close()

    @staticmethod
    def getSetting(key):

        settings = LocalAppManager.loadSettings()
        if key in settings:
            return settings[key]

        if key == "server_url":
            return "https://thunderklaud-api.web2ju.de/"
        if key == "local_sync_folder_path":
            return "./test/client/"

    @staticmethod
    def saveSetting(key, value):
        settings = LocalAppManager.loadSettings()
        settings[key] = value

        path = LocalAppManager.getLocalAppPath() + "settings.json"
        jsonFile = open(path, "w")
        settings = json.dumps(settings)
        jsonFile.write(settings)
        jsonFile.close()

    @staticmethod
    def saveSettings(settings):
        settings = json.dumps(settings)
        path = LocalAppManager.getLocalAppPath() + "settings.json"

        jsonFile = open(path, "w")
        jsonFile.write(settings)
        jsonFile.close()

    @staticmethod
    def loadSettings():
        path = LocalAppManager.getLocalAppPath() + "settings.json"
        jsonFile = open(path, "r")
        settings = {}
        settings = json.load(jsonFile)
        jsonFile.close()
        return settings

    @staticmethod
    def removeJWTLocally():
        localJWTPath = LocalAppManager.getLocalJWTPath()
        os.remove(localJWTPath)

    @staticmethod
    def doStartupActions():
        LocalAppManager.createLocalAppPathIfNotExists()
        LocalAppManager.createDefaultSettingsJson()
